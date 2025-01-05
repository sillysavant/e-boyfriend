# Created: dylannguyen
from typing import Literal
from sentence_transformers import SentenceTransformer
from azure.core.credentials import AzureKeyCredential  
#from azure.search.documents import SearchClient  
from azure.search.documents.aio import SearchClient
from azure.search.documents.models import (
    QueryAnswerType,
    QueryCaptionType,
    QueryType,
    VectorizedQuery,
)

from app.constant.config import AZURE_AI_SEARCH_KEY, AZURE_AI_SEARCH_URI

class CustomAzureSearch:
    def __init__(self,
        index_name: Literal["user_docs", "user_info"],
        number_results_to_return: int = 5,
        number_near_neighbors: int = 3,
        model_name: str = "all-MiniLM-L6-v2",
        embedding_field_name: str = "embedding",
        semantic_config_name: str = 'my-semantic-config'
    ):
        self.index_name = index_name
        self.model_name = model_name
        self.embedding_field_name = embedding_field_name
        self.number_results_to_return = number_results_to_return
        self.number_near_neighbors = number_near_neighbors
        self.semantic_config_name = semantic_config_name
        self.client = SearchClient(
            endpoint=AZURE_AI_SEARCH_URI, 
            index_name=self.index_name,
            credential=AzureKeyCredential(AZURE_AI_SEARCH_KEY)
        )

    async def get_vectorized_query(self, query, exhaustive_knn=False):

        """This returns a vectorized query

        Caters for both exhaustive knn queries and regular queries

        Steps:
            1. Gets the query as the input
            2. Gets the vector of the query using the model
            3. Returns the vectorized query
            3.1. If exhaustive_knn is True, then it returns an exhaustive knn query
            3.2. If exhaustive_knn is False, then it returns a regular knn query
        """
        query_vector = await self.get_embedding_query_vector(query)

        if exhaustive_knn:
            vector_query = VectorizedQuery(
                vector=query_vector, 
                k_nearest_neighbors=self.number_near_neighbors, 
                fields=self.embedding_field_name,
                exhaustive_knn =True
            )
        else:
            vector_query = VectorizedQuery(
                vector=query_vector, 
                k_nearest_neighbors=self.number_near_neighbors, 
                fields=self.embedding_field_name
            )
                               
        return vector_query

    async def get_embedding_query_vector(self, query: str):
        """Get the vector of the query

        Args:
            query (string): user input

        Returns:
            _type_: vector of the query
        """
        model = SentenceTransformer(self.model_name)
        query_vector = model.encode(query)
        return query_vector

    async def __get_results_to_return(self, results):

        """This returns the results to return
        """
        results_to_return = []
        async for result in results:
            results_to_return.append(
                {
                    "content": result["content"],
                    "createdat": result["createdat"],
                    "sourcefile": result["sourcefile"],
                }
            )
        return results_to_return
    
    async def get_results_vector_search(self, query: str, list_fields=None):
        
        """
        [summary]
        This returns the results of a vector search
        query: string
        list_fields: list of fields to return
        """
        
        vector_query = await self.get_vectorized_query(query)
        
        async with self.client:
            results = await self.client.search(  
                search_text=None,  
                vector_queries=[vector_query],
                select=list_fields,
                top=self.number_results_to_return,
            )  
        
            return await self.__get_results_to_return(results)
    
    async def get_results_hybrid_search(self, query: str, list_fields=None):
        
        """
        This returns the results of a hybrid search
        which is a combination of a vector search and a regular search

        Returns:
            Results of the query
        """
        
        vector_query = await self.get_vectorized_query(query)
        
        async with self.client:
            results = await self.client.search(  
                search_text=query,  
                vector_queries=[vector_query],
                select=list_fields,
                top=self.number_results_to_return,
            )  
            
            return await self.__get_results_to_return(results)
    
    async def get_results_exhaustive_knn(self, query: str, list_fields=None):
        
        """
        Provides the results of an exhaustive knn query

        Returns:
            [list,list]: results of the query
        """
        
        vector_query = await self.get_vectorized_query(query, exhaustive_knn=True)
        
        async with self.client:
            results = await self.client.search(  
                search_text=query,  
                vector_queries=[vector_query],
                select=list_fields,
                top=self.number_results_to_return,
            )  
            
            return await self.__get_results_to_return(results)
    
    async def get_results_semantic_search(self, query: str, list_fields=None):
        """Provides the results of a semantic search query

        Returns:
            _type_: results of the query
        """
        
        vector_query = await self.get_vectorized_query(query)
        
        async with self.client:
            results = await self.client.search(  
                    search_text=query,  
                    vector_queries=[vector_query],
                    select=list_fields,
                    query_type=QueryType.SEMANTIC, 
                    semantic_configuration_name=self.semantic_config_name, 
                    query_caption=QueryCaptionType.EXTRACTIVE, 
                    query_answer=QueryAnswerType.EXTRACTIVE,
                    top=self.number_results_to_return,
                )  
            
            return await self.__get_results_to_return(results)