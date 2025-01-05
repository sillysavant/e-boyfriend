# Created: dylannguyen
from io import BytesIO
from typing import Annotated, Literal
from fastapi import HTTPException, UploadFile, status
from app.utils.azure_blob_helper import AzureBlobHelper
from app.utils.azure_document_search import create_sections, get_document_text
from app.utils.azure_vector_search_index import upload_sections_to_azure_search_index

async def upload_docs(
    uploaded_file: UploadFile, 
    category: Annotated[str, "category of the uploaded file"], 
    index_name: Literal["user_docs", "user_info"]
):
    """
    Uploads a document to Azure Blob Storage, AI Search indexes
    """
    try:
        azure_blob = AzureBlobHelper()
        await azure_blob.upload_blob(upload_file=uploaded_file)
        await uploaded_file.seek(0)
        page_map = await get_document_text(uploaded_file=uploaded_file, use_local_parser=False)
        await uploaded_file.seek(0)
        #sections = await create_sections(filename= uploaded_file.filename, page_map=page_map, category=category)
        sections = []
        async for section in create_sections(
            filename=uploaded_file.filename,
            page_map=page_map,
            category=category
        ):
            sections.append(section)
        print("Created sections")
        await upload_sections_to_azure_search_index(index_name=index_name, sections=sections)
        print("Uploaded to Azure Search Index")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )