"""
Vector Store Tool for Agentic RAG System

This tool wraps the existing RAG system to provide university information
search capabilities within the LangGraph framework.
"""

import logging
import time
from typing import Dict, Any, Optional, List
from langchain.tools import tool
from langchain_core.language_models import BaseLanguageModel

# Import existing RAG system
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from rag_system import RAGSystem
from groq_llm import create_groq_service

logger = logging.getLogger(__name__)


class VectorStoreTool:
    """Tool for searching NIT KKR university information using existing RAG system."""
    
    def __init__(self, vector_store_path: str = "vector_store", llm: Optional[BaseLanguageModel] = None):
        """
        Initialize Vector Store Tool.
        
        Args:
            vector_store_path: Path to the vector store directory
            llm: Language model for response generation
        """
        self.vector_store_path = vector_store_path
        self.llm = llm
        self.rag_system = None
        self._initialize_rag_system()
        
    def _initialize_rag_system(self):
        """Initialize the existing RAG system."""
        try:
            # Create RAG system with existing configuration
            self.rag_system = RAGSystem(
                vector_store_path=self.vector_store_path,
                use_groq=True
            )
            logger.info("Vector Store Tool initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize RAG system: {e}")
            raise
    
    def search_university_info(self, query: str) -> str:
        """
        Search NIT KKR database for university-related information.
        
        Use for questions about:
        - Admission requirements and procedures
        - Course details and curriculum
        - Faculty information and qualifications  
        - Campus facilities and infrastructure
        - University policies and regulations
        - Department information
        - Placement statistics
        - Research programs
        
        Args:
            query: Specific question about NIT Kurukshetra
            
        Returns:
            Relevant information with source citations
        """
        start_time = time.time()
        
        try:
            if not self.rag_system:
                return "Error: RAG system not initialized. Please check vector store."
            
            # Use existing RAG system to get response
            response = self.rag_system.answer_query(query)
            
            execution_time = time.time() - start_time
            logger.info(f"Vector search completed in {execution_time:.2f}s")
            
            # Format response for agentic system
            # RAG system returns: {'query', 'response', 'sources', 'num_sources'}
            if isinstance(response, dict):
                formatted_response = response.get('response', response.get('answer', str(response)))
                sources = response.get('sources', [])
            else:
                formatted_response = str(response)
                sources = []
            
            logger.info(f"Vector search successful: {len(formatted_response)} chars, {len(sources)} sources")
            
            return formatted_response
            
        except Exception as e:
            logger.error(f"Error in vector store search: {e}")
            return f"Error searching university information: {str(e)}"
    
    def get_rag_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the RAG system.
        
        Returns:
            Dict[str, Any]: RAG system statistics
        """
        try:
            if not self.rag_system:
                return {"error": "RAG system not initialized"}
            
            # Get stats from existing RAG system
            stats = self.rag_system.get_stats() if hasattr(self.rag_system, 'get_stats') else {}
            
            return {
                "rag_system": "initialized",
                "vector_store_path": self.vector_store_path,
                "stats": stats
            }
            
        except Exception as e:
            logger.error(f"Error getting RAG stats: {e}")
            return {"error": str(e)}
    
    def test_connection(self) -> bool:
        """
        Test if the vector store tool is working properly.
        
        Returns:
            bool: True if tool is working
        """
        try:
            test_query = "What is NIT Kurukshetra?"
            result = self.search_university_info(test_query)
            
            # Check if we got a meaningful response
            is_working = (
                result and 
                len(result) > 50 and 
                "Error" not in result and
                "NIT" in result
            )
            
            logger.info(f"Vector search test: {'PASSED' if is_working else 'FAILED'}")
            return is_working
            
        except Exception as e:
            logger.error(f"Vector store tool test failed: {e}")
            return False


# Factory function
def create_vector_store_tool(
    vector_store_path: str = "vector_store", 
    llm: Optional[BaseLanguageModel] = None
) -> VectorStoreTool:
    """
    Factory function to create a Vector Store Tool.
    
    Args:
        vector_store_path: Path to vector store
        llm: Language model for responses
        
    Returns:
        VectorStoreTool: Configured vector store tool
    """
    return VectorStoreTool(vector_store_path, llm)


# LangChain tool wrapper function
@tool
def search_nit_kkr_database(query: str) -> str:
    """
    Search the NIT Kurukshetra database for university information.
    
    This tool provides access to comprehensive information about:
    - Academic programs and courses
    - Admission requirements and procedures
    - Faculty and departments
    - Campus facilities and infrastructure
    - Research and development activities
    - Placement and career services
    - Student life and activities
    
    Args:
        query: Your specific question about NIT Kurukshetra
        
    Returns:
        Detailed information with source citations from the university database
    """
    try:
        # Create tool instance
        tool = create_vector_store_tool()
        
        # Execute search
        result = tool.search_university_info(query)
        
        return result
        
    except Exception as e:
        logger.error(f"Error in NIT KKR database search: {e}")
        return f"Unable to search NIT KKR database: {str(e)}"


# Test function
def test_vector_store_tool():
    """
    Test the vector store tool functionality.
    """
    print("Testing Vector Store Tool...")
    
    try:
        # Create tool
        tool = create_vector_store_tool()
        
        # Test connection
        print("Testing connection...")
        is_connected = tool.test_connection()
        print(f"Connection test: {'PASSED' if is_connected else 'FAILED'}")
        
        if is_connected:
            # Test queries
            test_queries = [
                "What are the admission requirements for CSE?",
                "Tell me about the computer science department",
                "What facilities are available on campus?"
            ]
            
            for query in test_queries:
                print(f"\nQuery: {query}")
                result = tool.search_university_info(query)
                print(f"Result: {result[:200]}..." if len(result) > 200 else result)
        
        # Get stats
        stats = tool.get_rag_stats()
        print(f"\nRAG Stats: {stats}")
        
    except Exception as e:
        print(f"Test failed: {e}")


if __name__ == "__main__":
    # Run test if executed directly
    test_vector_store_tool()
