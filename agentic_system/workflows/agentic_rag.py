"""
Main Agentic RAG Workflow

This module contains the main workflow that orchestrates
all agents and tools for the agentic RAG system.
"""

import logging
import time
from typing import Dict, Any, Optional, List
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.language_models import BaseLanguageModel
from langgraph.graph import StateGraph, END, START

from ..workflows.state_management import AgenticState, QueryIntent
from ..agents.router_agent import RouterAgent, create_router_agent
from ..agents.evaluator_agent import EvaluatorAgent, create_evaluator_agent
from ..tools.vector_store_tool import search_nit_kkr_database
from ..tools.web_search_tool import search_real_time_info
from ..tools.calculator_tool import perform_calculation

logger = logging.getLogger(__name__)


class AgenticRAGWorkflow:
    """Main workflow orchestrator for agentic RAG system."""
    
    def __init__(self, llm: Optional[BaseLanguageModel] = None):
        """
        Initialize Agentic RAG Workflow.
        
        Args:
            llm: Language model to use for agents
        """
        self.llm = llm
        self.router_agent = create_router_agent(llm)
        self.evaluator_agent = create_evaluator_agent(llm)
        
        # Available tools
        self.tools = [
            search_nit_kkr_database,
            search_real_time_info,
            perform_calculation
        ]
        
        # Custom tool execution based on routing
        self.tool_map = {
            "vector_store": search_nit_kkr_database,
            "web_search": search_real_time_info,
            "calculator": perform_calculation
        }
        
        # Build the workflow graph
        self.workflow = self._build_workflow()
        self.graph = self.workflow.compile()
        
        logger.info("Agentic RAG Workflow initialized successfully")
    
    def _build_workflow(self) -> StateGraph:
        """
        Build LangGraph workflow with all nodes and edges.
        
        Returns:
            StateGraph: Configured workflow graph
        """
        # Create workflow with state
        workflow = StateGraph(AgenticState)
        
        # Add nodes
        workflow.add_node("router", self._route_query)
        workflow.add_node("tools", self._execute_tools)
        workflow.add_node("evaluator", self._evaluate_results)
        workflow.add_node("rewriter", self._rewrite_query)
        workflow.add_node("generator", self._generate_response)
        
        # Add edges
        workflow.add_edge(START, "router")
        
        # Router to tools or direct response
        workflow.add_conditional_edges(
            "router",
            self._should_use_tools,
            {
                "use_tools": "tools",
                "direct_response": "generator"
            }
        )
        
        # Tools to evaluator
        workflow.add_edge("tools", "evaluator")
        
        # Evaluator to rewriter or generator
        workflow.add_conditional_edges(
            "evaluator",
            self._should_continue_search,
            {
                "continue": "rewriter",
                "generate": "generator"
            }
        )
        
        # Rewriter back to router
        workflow.add_edge("rewriter", "router")
        
        # Generator to end
        workflow.add_edge("generator", END)
        
        return workflow
    
    def _ensure_state(self, state: Any) -> AgenticState:
        """Ensure state is an AgenticState object."""
        if isinstance(state, dict):
            return AgenticState(**state)
        return state

    def _route_query(self, state: Any) -> Dict[str, Any]:
        """
        Route query to appropriate tool based on intent.
        """
        state = self._ensure_state(state)
        try:
            logger.info("Routing query...")
            
            # Process query through router agent
            state = self.router_agent.process_query(state)
            
            # Add start time if not set
            if not state.start_time:
                state.start_time = time.time()
            
            logger.info(f"Query routed to: {state.current_tool}")
            return state.dict() if hasattr(state, 'dict') else state
            
        except Exception as e:
            logger.error(f"Error in query routing: {e}")
            # Fallback to vector store
            state.current_intent = QueryIntent.UNIVERSITY_INFO
            state.current_tool = "vector_store"
            return state
    
    def _should_use_tools(self, state: Any) -> str:
        """
        Determine if tools should be used or direct response.
        """
        state = self._ensure_state(state)
        # If no tool selected, use direct response
        if not state.current_tool:
            return "direct_response"
        
        # If tool is already used and we have context, check if we need more
        if state.retrieved_context and state.iteration_count > 0:
            return "direct_response"
        
        return "use_tools"
    
    def _execute_tools(self, state: Any) -> Dict[str, Any]:
        """
        Execute specific tool based on routing decision.
        """
        state = self._ensure_state(state)
        try:
            logger.info(f"Executing tool: {state.current_tool}")
            
            # Get the appropriate tool based on routing
            tool = self.tool_map.get(state.current_tool)
            if not tool:
                logger.error(f"Unknown tool: {state.current_tool}")
                return state
            
            user_query = state.get_last_user_message()
            
            # Each tool has different required parameters
            if state.current_tool == "calculator":
                tool_input = {"expression": user_query}
            else:
                tool_input = {"query": user_query}
            
            # Execute the tool
            tool_result = tool.invoke(tool_input)
            
            # Ensure result is a string
            if not isinstance(tool_result, str):
                tool_result = str(tool_result)
            
            # Update state with tool result
            state.retrieved_context = tool_result
            state.add_tool_usage(state.current_tool, 0.0)
            
            logger.info(f"Tool execution completed: {state.current_tool}")
            return state.dict() if hasattr(state, 'dict') else state
            
        except Exception as e:
            logger.error(f"Error in tool execution: {e}")
            state.retrieved_context = f"Tool error: {str(e)}"
            return state.dict() if hasattr(state, 'dict') else state
    
    def _evaluate_results(self, state: Any) -> Dict[str, Any]:
        """
        Evaluate retrieved information quality.
        """
        state = self._ensure_state(state)
        try:
            logger.info("Evaluating retrieved results...")
            
            # Process through evaluator agent
            state = self.evaluator_agent.process_evaluation(state)
            
            logger.info(f"Evaluation complete: should_continue={state.should_continue()}")
            return state.dict() if hasattr(state, 'dict') else state
            
        except Exception as e:
            logger.error(f"Error in result evaluation: {e}")
            # Set to not continue on error
            state.last_quality_score = 0.5
            return state
    
    def _should_continue_search(self, state: Any) -> str:
        """
        Determine if search should continue or generate response.
        """
        state = self._ensure_state(state)
        if state.should_continue():
            return "continue"
        else:
            return "generate"
    
    def _rewrite_query(self, state: Any) -> Dict[str, Any]:
        """
        Rewrite query for better search results.
        """
        state = self._ensure_state(state)
        try:
            logger.info("Rewriting query...")
            
            # Get original query and feedback
            original_query = state.get_last_user_message()
            
            if not state.quality_grades:
                logger.warning("No quality grades available for query rewriting")
                return state
            
            latest_grade = state.quality_grades[-1]
            feedback = latest_grade.improvement_suggestion
            
            # Simple query rewriting based on feedback
            rewritten_query = self._generate_improved_query(original_query, feedback)
            
            # Update the last message with rewritten query
            if state.messages:
                # Replace the last human message with rewritten query
                state.messages[-1] = HumanMessage(content=rewritten_query)
            
            logger.info(f"Query rewritten: {rewritten_query}")
            return state.dict() if hasattr(state, 'dict') else state
            
        except Exception as e:
            logger.error(f"Error in query rewriting: {e}")
            return state
    
    def _generate_improved_query(self, original_query: str, feedback: str) -> str:
        """
        Generate improved query based on feedback.
        
        Args:
            original_query: Original user query
            feedback: Quality evaluation feedback
            
        Returns:
            str: Improved query
        """
        # Simple heuristic improvements based on feedback
        improved_query = original_query.lower()
        
        if "specific" in feedback.lower():
            # Add more specific terms
            if "cse" not in improved_query:
                improved_query += " computer science engineering"
            if "admission" in improved_query:
                improved_query += " requirements eligibility criteria"
        
        elif "detailed" in feedback.lower():
            # Add detail-oriented terms
            if "fees" in improved_query:
                improved_query += " semester wise breakdown structure"
            elif "facility" in improved_query:
                improved_query += " amenities infrastructure details"
        
        elif "recent" in feedback.lower() or "current" in feedback.lower():
            # Add time-related terms
            improved_query += " 2024 latest updated"
        
        return improved_query
    
    def _generate_response(self, state: Any) -> Dict[str, Any]:
        """
        Generate final response based on accumulated context.
        """
        state = self._ensure_state(state)
        try:
            logger.info("Generating final response...")
            
            # Get user query and context
            user_query = state.get_last_user_message()
            context = state.retrieved_context
            
            if not context:
                response = "I apologize, but I couldn't find relevant information for your query. Please try rephrasing your question or contact the administration directly."
            else:
                # Generate response using context
                response = self._format_final_response(user_query, context, state)
            
            # Add AI message to conversation
            ai_message = AIMessage(content=response)
            state.messages.append(ai_message)
            
            # Update execution time
            if state.start_time:
                execution_time = time.time() - state.start_time
                logger.info(f"Response generated in {execution_time:.2f}s")
            
            return state.dict() if hasattr(state, 'dict') else state
            
        except Exception as e:
            logger.error(f"Error in response generation: {e}")
            error_response = "I encountered an error while generating your response. Please try again."
            state.messages.append(AIMessage(content=error_response))
            return state.dict() if hasattr(state, 'dict') else state
    
    def _format_final_response(self, query: str, context: str, state: AgenticState) -> str:
        """
        Use the LLM to synthesize a clean, natural-language response from the context.
        Falls back to a formatted plain-text answer if the LLM is unavailable.
        """
        intent = (state.current_intent or "university_info").lower()
        
        # Build a focused system prompt based on intent
        if "calculation" in intent:
            system_prompt = (
                "You are a helpful assistant. The user asked a math question. "
                "The calculation result is provided below. "
                "Respond with ONLY the direct answer — the numeric result and a one-sentence explanation. "
                "Do not repeat the question. Do not add extra commentary."
            )
        elif "real_time" in intent:
            system_prompt = (
                "You are a helpful assistant providing current information. "
                "Summarize the search results below into a clear, concise answer for the user. "
                "Do not repeat the question. Cite sources naturally when relevant."
            )
        else:
            system_prompt = (
                "You are a helpful assistant for NIT Kurukshetra. "
                "Answer the user's question using ONLY the information provided below. "
                "Be clear, direct, and well-structured. "
                "Do not repeat the question. If the information is incomplete, say so honestly."
            )
        
        try:
            if self.llm:
                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=f"Question: {query}\n\nRelevant Information:\n{context}")
                ]
                ai_response = self.llm.invoke(messages)
                return ai_response.content
        except Exception as e:
            logger.warning(f"LLM synthesis failed, falling back to raw context: {e}")
        
        # Fallback: return the context directly if LLM is unavailable
        return context
    
    def invoke(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Invoke the agentic workflow with input data.
        
        Args:
            input_data: Input data containing query and optional metadata
            
        Returns:
            Dict[str, Any]: Workflow results
        """
        try:
            # Prepare initial state
            query = input_data.get("query", "")
            session_id = input_data.get("session_id", None)
            
            initial_state = AgenticState(
                messages=[HumanMessage(content=query)],
                session_id=session_id
            )
            
            # Execute workflow
            logger.info(f"Starting agentic workflow for query: {query[:100]}...")
            result = self.graph.invoke(initial_state)
            
            # Extract final response
            final_response = ""
            
            # Handle result whether it's an object or a dict
            messages = []
            if hasattr(result, 'messages'):
                messages = result.messages
            elif isinstance(result, dict) and 'messages' in result:
                messages = result['messages']
            
            if messages:
                for message in reversed(messages):
                    # Check if it's an AI message (handle both object and dict)
                    m_type = ""
                    if hasattr(message, 'type'):
                        m_type = message.type
                    elif isinstance(message, dict):
                        m_type = message.get('type', '')
                    
                    if m_type == 'ai':
                        if hasattr(message, 'content'):
                            final_response = message.content
                        elif isinstance(message, dict):
                            final_response = message.get('content', '')
                        break
            
            # Prepare metadata safely
            def get_val(obj, key, default):
                if hasattr(obj, key):
                    return getattr(obj, key)
                if isinstance(obj, dict):
                    return obj.get(key, default)
                return default

            # Prepare output
            output = {
                "response": final_response,
                "session_id": session_id,
                "intent": get_val(result, "current_intent", "unknown"),
                "iterations": get_val(result, "iteration_count", 0),
                "tools_used": get_val(result, "tool_history", []),
                "quality_score": get_val(result, "last_quality_score", 0.0),
                "execution_time": time.time() - (get_val(result, "start_time", 0) or time.time()),
                "state_summary": result.get_summary() if hasattr(result, 'get_summary') else (result.get('get_summary', lambda: {})() if isinstance(result, dict) and 'get_summary' in result else {})
            }
            
            logger.info(f"Workflow completed: {len(final_response)} chars response")
            return output
            
        except Exception as e:
            logger.error(f"Error in workflow execution: {e}")
            return {
                "response": f"Error processing your query: {str(e)}",
                "error": str(e),
                "session_id": input_data.get("session_id")
            }
    
    def get_workflow_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the workflow.
        
        Returns:
            Dict[str, Any]: Workflow statistics
        """
        return {
            "workflow": "agentic_rag",
            "status": "initialized",
            "tools_count": len(self.tools),
            "tools": [tool.name for tool in self.tools],
            "nodes": ["router", "tools", "evaluator", "rewriter", "generator"],
            "router_agent": "initialized",
            "evaluator_agent": "initialized"
        }
    
    def stream(self, input_data: Dict[str, Any]):
        """
        Stream workflow execution for real-time updates.
        
        Args:
            input_data: Input data containing query
            
        Yields:
            Dict[str, Any]: Intermediate workflow states
        """
        try:
            # Prepare initial state
            query = input_data.get("query", "")
            session_id = input_data.get("session_id", None)
            
            initial_state = AgenticState(
                messages=[HumanMessage(content=query)],
                session_id=session_id
            )
            
            # Stream workflow execution
            logger.info(f"Streaming agentic workflow for query: {query[:100]}...")
            
            for chunk in self.graph.stream(initial_state):
                yield {
                    "type": "workflow_update",
                    "node": chunk.get("node", "unknown"),
                    "state": chunk.get("state", {}),
                    "session_id": session_id
                }
            
        except Exception as e:
            logger.error(f"Error in workflow streaming: {e}")
            yield {
                "type": "error",
                "error": str(e),
                "session_id": input_data.get("session_id")
            }


# Factory function
def create_agentic_rag_workflow(llm: Optional[BaseLanguageModel] = None) -> AgenticRAGWorkflow:
    """
    Factory function to create an Agentic RAG Workflow.
    
    Args:
        llm: Language model to use
        
    Returns:
        AgenticRAGWorkflow: Configured workflow
    """
    return AgenticRAGWorkflow(llm=llm)


# Test function
def test_agentic_workflow():
    """
    Test the agentic workflow functionality.
    """
    print("Testing Agentic RAG Workflow...")
    
    try:
        # Create workflow
        workflow = create_agentic_rag_workflow()
        
        # Test queries
        test_queries = [
            "What are the admission requirements for CSE?",
            "What's the current weather in Kurukshetra?",
            "Calculate total fees for 4 years B.Tech",
            "Compare CSE and ECE departments"
        ]
        
        for query in test_queries:
            print(f"\n{'='*50}")
            print(f"Query: {query}")
            
            # Execute workflow
            result = workflow.invoke({"query": query})
            
            print(f"Response: {result['response'][:200]}..." if len(result['response']) > 200 else result['response'])
            print(f"Intent: {result['intent']}")
            print(f"Tools: {result['tools_used']}")
            print(f"Iterations: {result['iterations']}")
            print(f"Quality: {result['quality_score']}")
            print(f"Time: {result['execution_time']:.2f}s")
        
        # Get workflow stats
        stats = workflow.get_workflow_stats()
        print(f"\nWorkflow Stats: {stats}")
        
    except Exception as e:
        print(f"Test failed: {e}")


if __name__ == "__main__":
    # Run test if executed directly
    test_agentic_workflow()
