"""
Rewriter Agent for Agentic RAG System

This agent is responsible for improving the user's query based on 
evaluation feedback when the initial search results are insufficient.
"""

import logging
from typing import Dict, Any, Optional
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.language_models import BaseLanguageModel
from langchain_groq import ChatGroq

from ..workflows.state_management import AgenticState
from ..utils.prompts import get_query_rewriter_prompt

logger = logging.getLogger(__name__)


class RewriterAgent:
    """Agent responsible for query rewriting and optimization."""
    
    def __init__(self, llm: Optional[BaseLanguageModel] = None):
        """
        Initialize the Rewriter Agent.
        
        Args:
            llm: Language model to use. Defaults to Groq.
        """
        self.llm = llm or ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0.2
        )
        self.system_prompt = get_query_rewriter_prompt()
        
    def rewrite_query(self, state: AgenticState) -> str:
        """
        Rewrite the query to get better results.
        
        Args:
            state: Current agentic state
            
        Returns:
            str: Rewritten query
        """
        try:
            # Get original query and feedback
            original_query = state.get_last_user_message()
            
            if not state.quality_grades:
                logger.warning("No quality grades found for rewriting")
                return original_query
            
            latest_grade = state.quality_grades[-1]
            feedback = latest_grade.improvement_suggestion
            context = state.retrieved_context
            
            # Create messages for the LLM
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=f"Original Query: {original_query}\nFeedback: {feedback}\nPrevious Context Preview: {context[:500]}")
            ]
            
            # Invoke LLM
            response = self.llm.invoke(messages)
            
            return response.content.strip()
            
        except Exception as e:
            logger.error(f"Error in query rewriting: {e}")
            return state.get_last_user_message() or ""
            
    def process_rewriting(self, state: AgenticState) -> AgenticState:
        """
        Process the rewriting step and update state.
        
        Args:
            state: Current agentic state
            
        Returns:
            AgenticState: Updated state with rewritten query
        """
        rewritten_query = self.rewrite_query(state)
        
        # Increment iteration count
        state.iteration_count += 1
        
        # Replace last human message with rewritten query for next iteration
        if state.messages:
            state.messages[-1] = HumanMessage(content=rewritten_query)
            
        logger.info(f"Query rewritten for iteration {state.iteration_count}: {rewritten_query}")
        
        return state


def create_rewriter_agent(llm: Optional[BaseLanguageModel] = None) -> RewriterAgent:
    """Factory function for Rewriter Agent."""
    return RewriterAgent(llm=llm)
