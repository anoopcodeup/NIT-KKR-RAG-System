"""
Intent Router Agent for Agentic RAG System

This agent is responsible for analyzing user queries and classifying them
into specific intents to determine which tools should be used.
"""

import logging
from typing import Dict, Any, Optional
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.language_models import BaseLanguageModel
from langchain_groq import ChatGroq

from ..workflows.state_management import (
    AgenticState, 
    QueryIntent, 
    IntentClassification
)
from ..utils.prompts import get_intent_router_prompt

logger = logging.getLogger(__name__)


class RouterAgent:
    """Agent responsible for intent classification and query routing."""
    
    def __init__(self, llm: Optional[BaseLanguageModel] = None):
        """
        Initialize the Router Agent.
        
        Args:
            llm: Language model to use for classification. Defaults to Groq.
        """
        self.llm = llm or ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0.1
        )
        self.system_prompt = get_intent_router_prompt()
        
    def classify_intent(self, query: str) -> IntentClassification:
        """
        Classify the intent of a user query.
        
        Args:
            query: The user's query string
            
        Returns:
            IntentClassification: The classified intent with metadata
        """
        try:
            # Create messages for the LLM
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=f"Query: {query}")
            ]
            
            # Get structured output from LLM
            structured_llm = self.llm.with_structured_output(IntentClassification)
            result = structured_llm.invoke(messages)
            
            logger.info(f"Intent classified: {result.intent} (confidence: {result.confidence})")
            return result
            
        except Exception as e:
            logger.error(f"Error in intent classification: {e}")
            # Fallback to university info intent
            return IntentClassification(
                intent=QueryIntent.UNIVERSITY_INFO,
                confidence=0.5,
                reasoning="Fallback due to classification error",
                required_tools=["vector_store"],
                complexity="simple"
            )
    
    def route_to_tool(self, intent: str) -> str:
        """
        Determine which tool to use based on intent.
        
        Args:
            intent: The classified intent (string)
            
        Returns:
            str: The name of the tool to use
        """
        # Normalize intent to lowercase
        intent_lower = intent.lower() if intent else "unknown"
        
        routing_map = {
            "university_info": "vector_store",
            "real_time_info": "web_search",
            "calculation": "calculator",
            "administrative": "scraper",
            "comparison": "multi_tool",
            "unknown": "vector_store"  # Default fallback
        }
        
        return routing_map.get(intent_lower, "vector_store")
    
    def get_required_tools(self, intent: str, complexity: str) -> list:
        """
        Get list of required tools based on intent and complexity.
        
        Args:
            intent: The classified intent (string)
            complexity: Query complexity level
            
        Returns:
            list: List of tool names required
        """
        # Normalize intent to lowercase
        intent_lower = intent.lower() if intent else "unknown"
        
        tool_map = {
            "university_info": ["vector_store"],
            "real_time_info": ["web_search"],
            "calculation": ["calculator"],
            "administrative": ["scraper"],
            "comparison": ["vector_store", "calculator"],
            "unknown": ["vector_store"]
        }
        
        # For complex queries, we might need additional tools
        if complexity == "complex" and intent_lower == "calculation":
            return ["vector_store", "calculator", "web_search"]
        
        return tool_map.get(intent_lower, ["vector_store"])
    
    def process_query(self, state: AgenticState) -> AgenticState:
        """
        Process a query and update state with routing information.
        
        Args:
            state: Current agentic state
            
        Returns:
            AgenticState: Updated state with routing information
        """
        try:
            # Get the last user message
            user_message = state.get_last_user_message()
            if not user_message:
                logger.warning("No user message found in state")
                state.current_intent = QueryIntent.UNKNOWN
                return state
            
            # Classify intent
            classification = self.classify_intent(user_message)
            
            # Update state
            state.current_intent = classification.intent
            state.intent_classification = classification
            state.current_tool = self.route_to_tool(classification.intent)
            
            # Add required tools to state
            required_tools = self.get_required_tools(
                classification.intent, 
                classification.complexity
            )
            state.tool_history.extend(required_tools)
            
            logger.info(f"Routed query to {state.current_tool} (intent: {classification.intent})")
            
            return state
            
        except Exception as e:
            logger.error(f"Error in query processing: {e}")
            # Fallback to vector store
            state.current_intent = QueryIntent.UNKNOWN
            state.current_tool = "vector_store"
            return state
    
    def validate_classification(self, classification: IntentClassification) -> bool:
        """
        Validate the classification result.
        
        Args:
            classification: The classification to validate
            
        Returns:
            bool: True if classification is valid
        """
        # Check confidence threshold
        if classification.confidence < 0.3:
            logger.warning(f"Low confidence classification: {classification.confidence}")
            return False
        
        # Check if intent is valid
        if classification.intent not in QueryIntent:
            logger.warning(f"Invalid intent: {classification.intent}")
            return False
        
        # Check if tools are specified
        if not classification.required_tools:
            logger.warning("No tools specified in classification")
            return False
        
        return True
    
    def get_routing_summary(self, state: AgenticState) -> Dict[str, Any]:
        """
        Get a summary of routing decisions for debugging.
        
        Args:
            state: Current agentic state
            
        Returns:
            Dict[str, Any]: Routing summary
        """
        return {
            "query": state.get_last_user_message(),
            "intent": state.current_intent,
            "confidence": state.intent_classification.confidence if state.intent_classification else 0.0,
            "reasoning": state.intent_classification.reasoning if state.intent_classification else "",
            "selected_tool": state.current_tool,
            "required_tools": state.intent_classification.required_tools if state.intent_classification else [],
            "complexity": state.intent_classification.complexity if state.intent_classification else "simple"
        }


# Utility functions
def create_router_agent(llm: Optional[BaseLanguageModel] = None) -> RouterAgent:
    """
    Factory function to create a Router Agent.
    
    Args:
        llm: Language model to use
        
    Returns:
        RouterAgent: Configured router agent
    """
    return RouterAgent(llm=llm)


def test_router_agent():
    """
    Test function for the Router Agent.
    """
    router = RouterAgent()
    
    test_queries = [
        "What are the admission requirements for CSE?",
        "What's the weather in Kurukshetra today?",
        "Calculate total fees for 4 years B.Tech",
        "Compare CSE and ECE departments"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        classification = router.classify_intent(query)
        tool = router.route_to_tool(classification.intent)
        print(f"Intent: {classification.intent}")
        print(f"Tool: {tool}")
        print(f"Confidence: {classification.confidence}")


if __name__ == "__main__":
    # Run test if executed directly
    test_router_agent()
