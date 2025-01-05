# Created: dylannguyen
from datetime import datetime
from io import BytesIO
import os
import re
from typing import AsyncGenerator, Dict
from fastapi import UploadFile
from pypdf import PdfReader, PdfWriter
#from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.ai.formrecognizer.aio import DocumentAnalysisClient
import html
from azure.core.credentials import AzureKeyCredential
from app.constant.config import AZURE_DOC_INTELL_KEY, AZURE_DOC_INTELL_URI, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_KEY
from tenacity import retry, wait_random_exponential, stop_after_attempt
from openai import AzureOpenAI
import asyncstdlib as a
from app.utils.azure_blob_helper import blob_name_from_file_page
MAX_SECTION_LENGTH = 1000
SENTENCE_SEARCH_LIMIT = 100
SECTION_OVERLAP = 100

async def table_to_html(table):
    table_html = "<table>"
    rows = [sorted([cell for cell in table.cells if cell.row_index == i], key=lambda cell: cell.column_index) for i in range(table.row_count)]
    for row_cells in rows:
        table_html += "<tr>"
        for cell in row_cells:
            tag = "th" if (cell.kind == "columnHeader" or cell.kind == "rowHeader") else "td"
            cell_spans = ""
            if cell.column_span > 1: cell_spans += f" colSpan={cell.column_span}"
            if cell.row_span > 1: cell_spans += f" rowSpan={cell.row_span}"
            table_html += f"<{tag}{cell_spans}>{html.escape(cell.content)}</{tag}>"
        table_html +="</tr>"
    table_html += "</table>"
    return table_html

async def get_document_text(uploaded_file: UploadFile, use_local_parser: bool = True):
    contents = await uploaded_file.read()
    input_pdf = BytesIO(contents)
    # Create a PDF writer and output buffer
    writer = PdfWriter()
    output_pdf = BytesIO()
    
    # Read the input PDF and copy pages to writer
    reader = PdfReader(input_pdf)
    for page in reader.pages:
        writer.add_page(page)
    
    # Write to the output buffer
    writer.write(output_pdf)
    output_pdf.seek(0)  # Reset buffer position
    
    offset = 0
    page_map = []
    if use_local_parser:
        reader = PdfReader(output_pdf)
        pages = reader.pages
        for page_num, p in enumerate(pages):
            page_text = p.extract_text()
            page_map.append((page_num, offset, page_text))
            offset += len(page_text)
    else:
        print(f"Extracting text from '{uploaded_file.filename}' using Azure Form Recognizer")
        docs_creds = AzureKeyCredential(key=AZURE_DOC_INTELL_KEY) 
        form_recognizer_client = DocumentAnalysisClient(
            endpoint=AZURE_DOC_INTELL_URI, 
            credential=docs_creds, 
            headers={"x-ms-useragent": "azure-search-chat-demo/1.0.0"}
        )
        
        async with form_recognizer_client:
            poller = await form_recognizer_client.begin_analyze_document(
               model_id="prebuilt-layout", 
               document=output_pdf
            )            
            form_recognizer_results = await poller.result()
            
            for page_num, page in enumerate(form_recognizer_results.pages):
                tables_on_page = [table for table in form_recognizer_results.tables if table.bounding_regions[0].page_number == page_num + 1]

                # mark all positions of the table spans in the page
                page_offset = page.spans[0].offset
                page_length = page.spans[0].length
                table_chars = [-1]*page_length
                for table_id, table in enumerate(tables_on_page):
                    for span in table.spans:
                        # replace all table spans with "table_id" in table_chars array
                        for i in range(span.length):
                            idx = span.offset - page_offset + i
                            if idx >=0 and idx < page_length:
                                table_chars[idx] = table_id

                # build page text by replacing characters in table spans with table html
                page_text = ""
                added_tables = set()
                for idx, table_id in enumerate(table_chars):
                    if table_id == -1:
                        page_text += form_recognizer_results.content[page_offset + idx]
                    elif not table_id in added_tables:
                        page_text += table_to_html(tables_on_page[table_id])
                        added_tables.add(table_id)

                page_text += " "
                page_map.append((page_num, offset, page_text))
                offset += len(page_text)

    return page_map

@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
# Function to generate embeddings for title and content fields, also used for query embeddings
async def generate_embeddings(
    text: str, 
    model: str ='text-embedding-3-small',
    dimensions: int = 384
):
    client = AzureOpenAI(
        api_key = AZURE_OPENAI_KEY,  
        api_version = "2023-05-15",
        azure_endpoint = AZURE_OPENAI_ENDPOINT
        )
    return client.embeddings.create(input = [text], model=model, dimensions=dimensions).data[0].embedding


async def split_text(page_map: list):
    SENTENCE_ENDINGS = [".", "!", "?"]
    WORDS_BREAKS = [",", ";", ":", " ", "(", ")", "[", "]", "{", "}", "\t", "\n"]

    def find_page(offset):
        l = len(page_map)
        for i in range(l - 1):
            if offset >= page_map[i][1] and offset < page_map[i + 1][1]:
                return i
        return l - 1

    all_text = "".join(p[2] for p in page_map)
    length = len(all_text)
    start = 0
    end = length
    while start + SECTION_OVERLAP < length:
        last_word = -1
        end = start + MAX_SECTION_LENGTH

        if end > length:
            end = length
        else:
            # Try to find the end of the sentence
            while end < length and (end - start - MAX_SECTION_LENGTH) < SENTENCE_SEARCH_LIMIT and all_text[end] not in SENTENCE_ENDINGS:
                if all_text[end] in WORDS_BREAKS:
                    last_word = end
                end += 1
            if end < length and all_text[end] not in SENTENCE_ENDINGS and last_word > 0:
                end = last_word # Fall back to at least keeping a whole word
        if end < length:
            end += 1

        # Try to find the start of the sentence or at least a whole word boundary
        last_word = -1
        while start > 0 and start > end - MAX_SECTION_LENGTH - 2 * SENTENCE_SEARCH_LIMIT and all_text[start] not in SENTENCE_ENDINGS:
            if all_text[start] in WORDS_BREAKS:
                last_word = start
            start -= 1
        if all_text[start] not in SENTENCE_ENDINGS and last_word > 0:
            start = last_word
        if start > 0:
            start += 1

        section_text = all_text[start:end]
        yield (section_text, find_page(start))

        last_table_start = section_text.rfind("<table")
        if (last_table_start > 2 * SENTENCE_SEARCH_LIMIT and last_table_start > section_text.rfind("</table")):
            # If the section ends with an unclosed table, we need to start the next section with the table.
            # If table starts inside SENTENCE_SEARCH_LIMIT, we ignore it, as that will cause an infinite loop for tables longer than MAX_SECTION_LENGTH
            # If last table starts inside SECTION_OVERLAP, keep overlapping
            print(f"Section ends with unclosed table, starting next section with the table at page {find_page(start)} offset {start} table start {last_table_start}")
            start = min(end - SECTION_OVERLAP, start + last_table_start)
        else:
            start = end - SECTION_OVERLAP
        
    if start + SECTION_OVERLAP < end:
        yield (all_text[start:end], find_page(start))
             
async def create_sections(filename: str, page_map: list, category: str) -> AsyncGenerator[Dict, None]:
    async for i, (section, pagenum) in a.enumerate(split_text(page_map)):
        yield {
            "id": re.sub("[^0-9a-zA-Z_-]","_",f"{filename}-{i}"),
            "content": section,
            "category": category,
            "createdat": datetime.utcnow().isoformat(timespec='seconds') + 'Z',
            "embedding": await generate_embeddings(section),
            "sourcepage": blob_name_from_file_page(filename=filename, page=pagenum),
            "sourcefile": filename
        }
