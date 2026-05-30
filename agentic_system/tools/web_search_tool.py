"""
Web Search Tool for Agentic RAG System

This tool provides real-time web search capabilities using Tavily API
for current information that may not be in the static vector store.
"""

import logging
import time
import os
from typing import Dict, Any, Optional, List
from langchain.tools import tool

try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Tavily not available. Install with: pip install tavily-python")

logger = logging.getLogger(__name__)


class WebSearchTool:
    """Tool for real-time web search using Tavily API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Web Search Tool.
        
        Args:
            api_key: Tavily API key. If None, tries to get from environment.
        """
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        self.client = None
        self._initialize_client()
        
    def _initialize_client(self):
        """Initialize Tavily client."""
        if not TAVILY_AVAILABLE:
            raise ImportError("Tavily not installed. Run: pip install tavily-python")
        
        if not self.api_key:
            raise ValueError("Tavily API key not found. Set TAVILY_API_KEY environment variable.")
        
        try:
            self.client = TavilyClient(api_key=self.api_key)
            logger.info("Web Search Tool initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Tavily client: {e}")
            raise
    
    def search_web(self, query: str) -> str:
        """
        Search the internet for real-time information.
        
        Use for questions about:
        - Current weather conditions
        - Recent news and announcements
        - Upcoming events and schedules
        - Latest rankings and achievements
        - Current admission dates and deadlines
        - Real-time status updates
        - Recent policy changes
        - Current market or industry trends
        
        Args:
            query: Real-time search query
            
        Returns:
            Current web search results with sources
        """
        start_time = time.time()
        
        try:
            if not self.client:
                return "Error: Web search client not initialized. Please check API key."
            
            # Perform search with Tavily
            search_result = self.client.search(
                query=query,
                search_depth="advanced",
                include_answer=True,
                include_raw_content=False,
                max_results=5
            )
            
            execution_time = time.time() - start_time
            
            # Format results
            formatted_results = self._format_search_results(search_result)
            
            # Add execution metadata
            metadata = {
                "tool": "web_search",
                "execution_time": execution_time,
                "results_count": len(search_result.get("results", [])),
                "query": query
            }
            
            logger.info(f"Web search completed in {execution_time:.2f}s: {len(search_result.get('results', []))} results")
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error in web search: {e}")
            return f"Error performing web search: {str(e)}"
    
    def _format_search_results(self, search_result: Dict[str, Any]) -> str:
        """
        Format search results into readable text.
        
        Args:
            search_result: Raw search results from Tavily
            
        Returns:
            str: Formatted search results
        """
        try:
            results = search_result.get("results", [])
            answer = search_result.get("answer")
            
            if not results and not answer:
                return "No results found for the search query."
            
            formatted_text = ""
            if answer:
                formatted_text += f"**Direct Answer:** {answer}\n\n"
                
            formatted_text += "Web Search Results:\n\n"
            
            for i, result in enumerate(results, 1):
                title = result.get("title", "No title")
                content = result.get("content", "No content available")
                url = result.get("url", "No URL")
                
                formatted_text += f"{i}. {title}\n"
                formatted_text += f"   {content[:300]}{'...' if len(content) > 300 else ''}\n"
                formatted_text += f"   Source: {url}\n\n"
            
            return formatted_text
            
        except Exception as e:
            logger.error(f"Error formatting search results: {e}")
            return "Error formatting search results."
    
    def get_search_stats(self) -> Dict[str, Any]:
        """
        Get statistics about web search tool.
        
        Returns:
            Dict[str, Any]: Tool statistics
        """
        return {
            "tool": "web_search",
            "status": "initialized" if self.client else "not_initialized",
            "api_key_set": bool(self.api_key),
            "tavily_available": TAVILY_AVAILABLE
        }
    
    def test_connection(self) -> bool:
        """
        Test if web search tool is working properly.
        
        Returns:
            bool: True if tool is working
        """
        try:
            if not self.client:
                return False
            
            # Test with a simple query
            test_query = "current time"
            result = self.search_web(test_query)
            
            # Check if we got meaningful results
            is_working = (
                result and 
                len(result) > 20 and 
                "Error" not in result
            )
            
            logger.info(f"Web search tool test: {'PASSED' if is_working else 'FAILED'}")
            return is_working
            
        except Exception as e:
            logger.error(f"Web search tool test failed: {e}")
            return False


# Factory function
def create_web_search_tool(api_key: Optional[str] = None) -> WebSearchTool:
    """
    Factory function to create a Web Search Tool.
    
    Args:
        api_key: Tavily API key
        
    Returns:
        WebSearchTool: Configured web search tool
    """
    return WebSearchTool(api_key=api_key)


# LangChain tool wrapper function
@tool
def search_real_time_info(query: str) -> str:
    """
    Search the internet for current real-time information.
    
    This tool provides access to:
    - Current weather conditions and forecasts
    - Latest news and announcements
    - Recent events and developments
    - Current market trends and statistics
    - Live status updates
    - Recent policy changes or updates
    
    Perfect for questions that require up-to-date information not available
    in static university databases.
    
    Args:
        query: Your question about current events or real-time information
        
    Returns:
        Latest information from web sources with citations
    """
    try:
        # Create tool instance
        tool = create_web_search_tool()
        
        # Execute search
        result = tool.search_web(query)
        
        return result
        
    except Exception as e:
        logger.error(f"Error in real-time web search: {e}")
        return f"Unable to search for real-time information: {str(e)}"


# Test function
def test_web_search_tool():
    """
    Test web search tool functionality.
    """
    print("Testing Web Search Tool...")
    
    try:
        # Check if Tavily is available
        if not TAVILY_AVAILABLE:
            print("Tavily not installed. Install with: pip install tavily-python")
            return
        
        # Check for API key
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            print("TAVILY_API_KEY environment variable not set")
            print("Get API key from: https://tavily.com/")
            return
        
        # Create tool
        tool = create_web_search_tool()
        
        # Test connection
        print("Testing connection...")
        is_connected = tool.test_connection()
        print(f"Connection test: {'PASSED' if is_connected else 'FAILED'}")
        
        if is_connected:
            # Test queries
            test_queries = [
                "current weather in Kurukshetra",
                "latest NIT KKR news",
                "engineering college rankings 2024"
            ]
            
            for query in test_queries:
                print(f"\nQuery: {query}")
                result = tool.search_web(query)
                print(f"Result: {result[:300]}..." if len(result) > 300 else result)
        
        # Get stats
        stats = tool.get_search_stats()
        print(f"\nWeb Search Stats: {stats}")
        
    except Exception as e:
        print(f"Test failed: {e}")


if __name__ == "__main__":
    # Run test if executed directly
    test_web_search_tool()
