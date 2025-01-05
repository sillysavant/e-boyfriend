# Created: dylannguyen
import json
import os
import re
from typing import Any, Generator
from azure.core.credentials import AzureKeyCredential  
from azure.search.documents import SearchClient  
from azure.search.documents.indexes import SearchIndexClient  
from azure.search.documents.indexes.models import (  
    ExhaustiveKnnAlgorithmConfiguration,
    ExhaustiveKnnParameters,
    SearchIndex,  
    SearchField,  
    SearchFieldDataType,  
    SimpleField,  
    SearchableField,  
    SearchIndex,  
    SemanticConfiguration,  
    SemanticPrioritizedFields,
    SemanticField,  
    SearchField,  
    SemanticSearch,
    VectorSearch,  
    HnswAlgorithmConfiguration,
    HnswParameters,  
    VectorSearch,
    VectorSearchAlgorithmConfiguration,
    VectorSearchAlgorithmKind,
    VectorSearchProfile,
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    VectorSearch,
    ExhaustiveKnnParameters,
    SearchIndex,  
    SearchField,  
    SearchFieldDataType,  
    SimpleField,  
    SearchableField,  
    SearchIndex,  
    SemanticConfiguration,  
    SemanticField,  
    SearchField,  
    VectorSearch,  
    HnswParameters,  
    VectorSearch,
    VectorSearchAlgorithmKind,
    VectorSearchAlgorithmMetric,
    VectorSearchProfile,
)  
from app.constant.config import *


async def create_azure_vector_search_index(index_name: str):
    """
        Currently, only use this function to create 2 indexes: user_info and user_docs
    """
    credential = AzureKeyCredential(AZURE_AI_SEARCH_KEY)
    index_client = SearchIndexClient(endpoint=AZURE_AI_SEARCH_URI, credential=credential)
    
    # document fields
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, 
                    key=True, sortable=True, 
                    filterable=True, facetable=True),
        SimpleField(name="category", type="Edm.String", filterable=True, facetable=True),
        SimpleField(name="createdat", type="Edm.DateTimeOffset", filterable=True, facetable=True, sortable=True),
        SearchableField(name="content", type="Edm.String", analyzer_name="en.microsoft"),
        SearchableField(name="sourcefile", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SimpleField(name="sourcepage", type="Edm.String", filterable=True, facetable=True),
        SearchField(name="embedding", type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True, vector_search_dimensions=384, 
                    vector_search_profile_name="myHnswProfile"),
    ]
    
    # Configure the vector search configuration  
    vector_search = VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(
                name="myHnsw",
                kind=VectorSearchAlgorithmKind.HNSW,
                parameters=HnswParameters(
                    m=4,
                    ef_construction=400,
                    ef_search=500,
                    metric=VectorSearchAlgorithmMetric.COSINE
                )
            ),
            ExhaustiveKnnAlgorithmConfiguration(
                name="myExhaustiveKnn",
                kind=VectorSearchAlgorithmKind.EXHAUSTIVE_KNN,
                parameters=ExhaustiveKnnParameters(
                    metric=VectorSearchAlgorithmMetric.COSINE
                )
            )
        ],
        profiles=[
            VectorSearchProfile(
                name="myHnswProfile",
                algorithm_configuration_name="myHnsw",
            ),
            VectorSearchProfile(
                name="myExhaustiveKnnProfile",
                algorithm_configuration_name="myExhaustiveKnn",
            )
        ]
    )
    
    # Configure the semantic search configuration  
    semantic_config = SemanticConfiguration(
        name="my-semantic-config",
        prioritized_fields=SemanticPrioritizedFields(
            content_fields=[SemanticField(field_name="content")],
            keywords_fields=[SemanticField(field_name="sourcefile")]
        )
    )
    
    # Create the semantic settings with the configuration
    semantic_search = SemanticSearch(configurations=[semantic_config])
    # Create the search index with the semantic settings
    index = SearchIndex(
        name=index_name, 
        fields=fields,
        vector_search=vector_search,
        semantic_search=semantic_search
    )

    result = index_client.create_or_update_index(index)
    
    return result

async def upload_sections_to_azure_search_index(index_name:str, sections: list):
    print(f"Uploading {len(sections)} sections to search index '{index_name}'")
    credential = AzureKeyCredential(AZURE_AI_SEARCH_KEY)
    search_client = SearchClient(
        endpoint=AZURE_AI_SEARCH_URI,
        index_name=index_name,
        credential=credential)
    
    i = 0
    batch = []
    for s in sections:
        batch.append(s)
        i += 1
        if i % 1000 == 0:
            results = search_client.upload_documents(documents=batch)
            succeeded = sum([1 for r in results if r.succeeded])
            print(f"\tIndexed {len(results)} sections, {succeeded} succeeded")
            batch = []

    if len(batch) > 0:
        results = search_client.upload_documents(documents=batch)
        succeeded = sum([1 for r in results if r.succeeded])
        print(f"\tIndexed {len(results)} sections, {succeeded} succeeded")


async def remove_from_azure_search_index(filename: str, index_name:str):
    print(f"Removing sections from '{filename or '<all>'}' from search index '{index_name}'")
    credential = AzureKeyCredential(AZURE_AI_SEARCH_KEY)
    search_client = SearchClient(endpoint=AZURE_AI_SEARCH_URI, index_name=index_name, credential=credential)
    while True:
        filter = None if filename == None else f"sourcefile eq '{os.path.basename(filename)}'"
        search_res = search_client.search("", filter=filter, top=1000, include_total_count=True)
        if search_res.get_count() == 0:
            break
        res = search_client.delete_documents(documents=[{ "id": doc["id"] } for doc in search_res])
        print(f"\tRemoved {len(res)} sections from index")
 
