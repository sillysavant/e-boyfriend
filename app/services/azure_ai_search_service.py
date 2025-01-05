# Created: dylannguyen
from typing_extensions import Annotated, Literal
from app.constant.config import AZURE_AI_SEARCH_INDEX_NAME, AZURE_AI_SEARCH_KEY, AZURE_AI_SEARCH_URI
from app.schema.search import SearchResponse
from app.utils.azure_ai_vector_search import CustomAzureSearch

async def get_results_vector_search(
        query: Annotated[str, "The query to search for"],
        index_name: Annotated[Literal["user_docs","user_info"], "user_docs for uploaded documents or user_info for user information"],
        number_near_neighbors: Annotated[int, "Number of nearest neighbors to return as top hits"] = 3,
        number_results_to_return: Annotated[int,"The number of search results to retrieve"] = 5,
        hybrid: Annotated[bool, "Choose hybrid search or not"] = False,
        exhaustive_knn: Annotated[bool, "Choose exhaustive KNN search or not"] = False,
        semantic_search: Annotated[bool, "Choose semantic search or not"] = True,
        list_of_fields: Annotated[list[str], "List of returned data fields"]= ["content","sourcefile", "createdat"],
        embedding_field_name: Annotated[str, "field contains embedding"] = "embedding",
        semantic_config_name: Annotated[str, "semantic configuration name"] ='my-semantic-config'
) -> list[Annotated[SearchResponse, "Most relevant search results"]]:
    """
    This function performs vector-based searches on a specified index using different search modes
    and configurations. 
    
    Options for the search modes:
    - pure vector search: Conducts a standard vector-based search.
    - hybrid: Combines traditional keyword and vector searches.
    - exhaustive_knn: Searches exhaustively for the nearest neighbors.
    - semantic_search (default): Performs semantic search for query understanding.

    Parameters:
        query (str): The input query string to search for.
        index_name (Literal["user_docs", "user_info"]): Specifies the index for the search.
            - "user_docs": Search within uploaded documents.
            - "user_info": Search within user information.
        number_near_neighbors (int): Number of nearest neighbors to return as top hits. Default is 3.
        number_results_to_return (int): Number of results to return from the search. Default is 5.
        hybrid (bool): Enable hybrid search. Default is False.
        exhaustive_knn (bool): Enable exhaustive KNN search. Default is False.
        semantic_search (bool): Enable semantic search. Default is True.
        list_of_fields (list): The list of fields to retrieve. Default is ["content", "sourcefile", "createdat"].
        embedding_field_name (str): Name of the field containing vector embeddings. Default is "embedding".
        semantic_config_name (str): Name of the semantic configuration to use. Default is "my-semantic-config".
    
    Returns:
        tuple: A tuple containing:
            - results_content (list): List of primary contents of the search results.
            - results_source (list): List of source information corresponding to the search results.
    """

    custom_azure_search = CustomAzureSearch(
        index_name=index_name,
        number_results_to_return=number_results_to_return,
        number_near_neighbors=number_near_neighbors,
        model_name = "all-MiniLM-L6-v2",
        embedding_field_name = embedding_field_name,
        semantic_config_name = semantic_config_name)

    if hybrid:
        results_content = await custom_azure_search.get_results_hybrid_search(query,list_of_fields)
    elif exhaustive_knn:  
        results_content = await custom_azure_search.get_results_exhaustive_knn(query,list_of_fields)
    elif semantic_search:
        results_content = await custom_azure_search.get_results_semantic_search(query,list_of_fields)
    else:
        results_content = await custom_azure_search.get_results_vector_search(query,list_of_fields)

    return results_content