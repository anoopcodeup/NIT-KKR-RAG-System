"""
Quality Evaluator Agent for Agentic RAG System

This agent is responsible for evaluating the quality and relevance of retrieved
information to determine if it sufficiently answers the user's question.
"""

import logging
from typing import Dict, Any, Optional
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.language_models import BaseLanguageModel
from langchain_groq import ChatGroq

from ..workflows.state_management import (
    AgenticState, 
    QualityGrade
)
from ..utils.prompts import get_quality_evaluator_prompt

logger = logging.getLogger(__name__)


class EvaluatorAgent:
    """Agent responsible for quality assessment and self-reflection."""
    
    def __init__(self, llm: Optional[BaseLanguageModel] = None):
        """
        Initialize Evaluator Agent.
        
        Args:
            llm: Language model to use for evaluation. Defaults to Groq.
        """
        self.llm = llm or ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0.1
        )
        self.system_prompt = get_quality_evaluator_prompt()
        self.quality_threshold = 0.7
        
    def evaluate_retrieved_info(self, query: str, context: str) -> QualityGrade:
        """
        Evaluate the quality and relevance of retrieved information.
        
        Args:
            query: The original user query
            context: The retrieved information/context
            
        Returns:
            QualityGrade: Quality assessment with scores and recommendations
        """
        try:
            # Create evaluation prompt
            evaluation_prompt = f"""
            Query: {query}
            
            Retrieved Context:
            {context}
            
            Please evaluate this information based on the criteria provided in the system prompt.
            """
            
            # Create messages for LLM
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=evaluation_prompt)
            ]
            
            # Get structured output from LLM
            structured_llm = self.llm.with_structured_output(QualityGrade)
            result = structured_llm.invoke(messages)
            
            logger.info(f"Quality evaluation: relevance={result.relevance_score:.2f}, "
                       f"completeness={result.completeness_score:.2f}, "
                       f"should_continue={result.should_continue}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in quality evaluation: {e}")
            # Fallback to moderate quality
            return QualityGrade(
                relevance_score=0.5,
                completeness_score=0.5,
                freshness_score=0.5,
                should_continue="no",
                improvement_suggestion="Unable to evaluate quality, proceeding with current information"
            )
    
    def should_continue_search(self, quality_grade: QualityGrade, threshold: float = None) -> bool:
        """
        Determine if search should continue based on quality assessment.
        
        Args:
            quality_grade: The quality assessment
            threshold: Quality threshold to use (defaults to instance threshold)
            
        Returns:
            bool: True if search should continue
        """
        if threshold is None:
            threshold = self.quality_threshold
            
        # Continue if any score is below threshold
        min_score = min(
            quality_grade.relevance_score,
            quality_grade.completeness_score,
            quality_grade.freshness_score
        )
        
        should_continue = (
            min_score < threshold or 
            quality_grade.should_continue.lower() == "yes"
        )
        
        logger.info(f"Continue search decision: {should_continue} (min_score: {min_score:.2f})")
        return should_continue
    
    def get_improvement_suggestion(self, quality_grade: QualityGrade) -> str:
        """
        Get specific improvement suggestion based on quality assessment.
        
        Args:
            quality_grade: The quality assessment
            
        Returns:
            str: Specific improvement suggestion
        """
        if quality_grade.relevance_score < 0.5:
            return "Try using more specific keywords related to NIT KKR programs, departments, or facilities"
        
        elif quality_grade.completeness_score < 0.5:
            return "Search for more detailed information including specific requirements, procedures, or contact details"
        
        elif quality_grade.freshness_score < 0.5:
            return "Look for more recent information or check official NIT KKR website for updates"
        
        else:
            return quality_grade.improvement_suggestion
    
    def evaluate_multiple_sources(self, query: str, contexts: list) -> QualityGrade:
        """
        Evaluate multiple retrieved sources and provide combined assessment.
        
        Args:
            query: The original user query
            contexts: List of retrieved contexts
            
        Returns:
            QualityGrade: Combined quality assessment
        """
        if not contexts:
            return QualityGrade(
                relevance_score=0.0,
                completeness_score=0.0,
                freshness_score=0.0,
                should_continue="yes",
                improvement_suggestion="No information found, try different search terms"
            )
        
        # Evaluate each context
        grades = []
        for context in contexts:
            grade = self.evaluate_retrieved_info(query, context)
            grades.append(grade)
        
        # Combine scores (average)
        avg_relevance = sum(g.relevance_score for g in grades) / len(grades)
        avg_completeness = sum(g.completeness_score for g in grades) / len(grades)
        avg_freshness = sum(g.freshness_score for g in grades) / len(grades)
        
        # Use the best improvement suggestion
        best_grade = max(grades, key=lambda g: g.relevance_score)
        
        # Determine if should continue based on best score
        should_continue = "no" if max(g.relevance_score for g in grades) > self.quality_threshold else "yes"
        
        return QualityGrade(
            relevance_score=avg_relevance,
            completeness_score=avg_completeness,
            freshness_score=avg_freshness,
            should_continue=should_continue,
            improvement_suggestion=best_grade.improvement_suggestion
        )
    
    def process_evaluation(self, state: AgenticState) -> AgenticState:
        """
        Process quality evaluation and update state.
        
        Args:
            state: Current agentic state
            
        Returns:
            AgenticState: Updated state with evaluation results
        """
        try:
            # Get query and context from state
            query = state.get_last_user_message()
            context = state.retrieved_context
            
            if not query:
                logger.warning("No query found in state for evaluation")
                return state
            
            if not context:
                logger.warning("No context found in state for evaluation")
                # Set low quality to trigger search
                quality_grade = QualityGrade(
                    relevance_score=0.0,
                    completeness_score=0.0,
                    freshness_score=0.0,
                    should_continue="yes",
                    improvement_suggestion="No information retrieved, try different search approach"
                )
            else:
                # Evaluate the retrieved information
                quality_grade = self.evaluate_retrieved_info(query, context)
            
            # Add quality grade to state
            state.add_quality_grade(quality_grade)
            
            # Update iteration count if continuing
            if self.should_continue_search(quality_grade):
                state.iteration_count += 1
            
            logger.info(f"Evaluation complete: should_continue={quality_grade.should_continue}")
            
            return state
            
        except Exception as e:
            logger.error(f"Error in evaluation processing: {e}")
            # Add fallback quality grade
            fallback_grade = QualityGrade(
                relevance_score=0.5,
                completeness_score=0.5,
                freshness_score=0.5,
                should_continue="no",
                improvement_suggestion="Evaluation error, proceeding with current information"
            )
            state.add_quality_grade(fallback_grade)
            return state
    
    def get_evaluation_summary(self, state: AgenticState) -> Dict[str, Any]:
        """
        Get a summary of evaluation results for debugging.
        
        Args:
            state: Current agentic state
            
        Returns:
            Dict[str, Any]: Evaluation summary
        """
        if not state.quality_grades:
            return {
                "evaluations": 0,
                "average_quality": 0.0,
                "should_continue": False
            }
        
        latest_grade = state.quality_grades[-1]
        avg_relevance = sum(g.relevance_score for g in state.quality_grades) / len(state.quality_grades)
        
        return {
            "evaluations": len(state.quality_grades),
            "latest_relevance": latest_grade.relevance_score,
            "latest_completeness": latest_grade.completeness_score,
            "latest_freshness": latest_grade.freshness_score,
            "average_quality": avg_relevance,
            "should_continue": latest_grade.should_continue == "yes",
            "improvement_suggestion": latest_grade.improvement_suggestion
        }


# Utility functions
def create_evaluator_agent(llm: Optional[BaseLanguageModel] = None) -> EvaluatorAgent:
    """
    Factory function to create an Evaluator Agent.
    
    Args:
        llm: Language model to use
        
    Returns:
        EvaluatorAgent: Configured evaluator agent
    """
    return EvaluatorAgent(llm=llm)


def test_evaluator_agent():
    """
    Test function for Evaluator Agent.
    """
    evaluator = EvaluatorAgent()
    
    test_cases = [
        {
            "query": "CSE admission requirements",
            "context": "NIT KKR offers B.Tech in CSE with 120 seats. Admission through JEE Main."
        },
        {
            "query": "Hostel facilities",
            "context": "NIT KKR provides separate hostels for boys and girls with WiFi, mess facilities, 24/7 security, and recreation rooms. Rooms are available on twin-sharing basis."
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"Query: {case['query']}")
        print(f"Context: {case['context']}")
        
        grade = evaluator.evaluate_retrieved_info(case['query'], case['context'])
        print(f"Relevance: {grade.relevance_score:.2f}")
        print(f"Completeness: {grade.completeness_score:.2f}")
        print(f"Should Continue: {grade.should_continue}")
        print(f"Suggestion: {grade.improvement_suggestion}")


if __name__ == "__main__":
    # Run test if executed directly
    test_evaluator_agent()
