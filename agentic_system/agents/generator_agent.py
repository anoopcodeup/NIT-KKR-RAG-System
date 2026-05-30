"""
Generator Agent for Agentic RAG System

This agent is responsible for synthesizing the final response based on 
the retrieved context and user query.
"""

import logging
from typing import Dict, Any, Optional, List
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.language_models import BaseLanguageModel
from langchain_groq import ChatGroq

from ..workflows.state_management import AgenticState
from ..utils.prompts import get_generator_prompt

logger = logging.getLogger(__name__)


class GeneratorAgent:
    """Agent responsible for generating the final response."""
    
    def __init__(self, llm: Optional[BaseLanguageModel] = None):
        """
        Initialize the Generator Agent.
        
        Args:
            llm: Language model to use. Defaults to Groq.
        """
        self.llm = llm or ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0.3
        )
        self.system_prompt = get_generator_prompt()
        
    def generate_response(self, state: AgenticState) -> str:
        """
        Generate final response based on context and query.
        
        Args:
            state: Current agentic state
            
        Returns:
            str: Generated response
        """
        try:
            # Get query and context
            query = state.get_last_user_message()
            context = state.retrieved_context
            
            if not context or "Error" in context:
                return "I apologize, but I couldn't find relevant information for your query. Please try rephrasing your question or contact the administration directly."
            
            # Create messages for the LLM
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=f"Context: {context}\n\nQuery: {query}")
            ]
            
            # Invoke LLM
            response = self.llm.invoke(messages)
            
            return response.content
            
        except Exception as e:
            logger.error(f"Error in response generation: {e}")
            return f"I encountered an error while generating the response: {str(e)}"
    
    def process_generation(self, state: AgenticState) -> AgenticState:
        """
        Process the generation step and update state.
        
        Args:
            state: Current agentic state
            
        Returns:
            AgenticState: Updated state with response
        """
        response = self.generate_response(state)
        
        # Add AI message to state
        state.messages.append(AIMessage(content=response))
        
        return state


def create_generator_agent(llm: Optional[BaseLanguageModel] = None) -> GeneratorAgent:
    """Factory function for Generator Agent."""
    return GeneratorAgent(llm=llm)
