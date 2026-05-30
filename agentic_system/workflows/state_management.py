"""
State Management for Agentic RAG System

This module defines the state schemas and data structures used throughout
the agentic workflow for maintaining context and tracking progress.
"""

from typing import List, Dict, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage


class QueryIntent(str, Enum):
    """Enumeration of possible query intents."""
    UNIVERSITY_INFO = "university_info"      # Use vector store
    REAL_TIME_INFO = "real_time_info"        # Use web search
    CALCULATION = "calculation"               # Use calculator
    ADMINISTRATIVE = "administrative"         # Use admin tools
    COMPARISON = "comparison"                 # Multi-tool required
    UNKNOWN = "unknown"                       # Fallback to vector store


class IntentClassification(BaseModel):
    """Schema for intent classification results."""
    intent: str = Field(..., description="Classified intent of query")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score")
    reasoning: str = Field(..., description="Reasoning for classification")
    required_tools: List[str] = Field(default_factory=list, description="Tools needed")
    complexity: str = Field(default="simple", description="Query complexity level")


class QualityGrade(BaseModel):
    """Schema for document quality evaluation."""
    relevance_score: float = Field(..., ge=0, le=1, description="Relevance to user query")
    completeness_score: float = Field(..., ge=0, le=1, description="How completely it answers")
    freshness_score: float = Field(..., ge=0, le=1, description="How current the information is")
    should_continue: str = Field(..., description="Whether to continue searching")
    improvement_suggestion: str = Field(..., description="How to improve the search")


class AgenticState(BaseModel):
    """Main state schema for the agentic RAG workflow."""
    # Core conversation
    messages: List[BaseMessage] = Field(default_factory=list, description="Conversation history")
    
    # Intent and routing
    current_intent: Optional[str] = Field(default=None, description="Current query intent")
    intent_classification: Optional[IntentClassification] = Field(default=None, description="Detailed classification")
    
    # Iteration control
    iteration_count: int = Field(default=0, description="Current iteration number")
    max_iterations: int = Field(default=3, description="Maximum allowed iterations")
    quality_threshold: float = Field(default=0.7, description="Quality threshold for stopping")
    
    # Tool usage tracking
    tool_history: List[str] = Field(default_factory=list, description="Tools used in this session")
    current_tool: Optional[str] = Field(default=None, description="Currently active tool")
    
    # Quality and evaluation
    last_quality_score: float = Field(default=0.0, description="Quality score of last result")
    quality_grades: List[QualityGrade] = Field(default_factory=list, description="History of quality evaluations")
    
    # Results and context
    retrieved_context: str = Field(default="", description="Currently retrieved information")
    accumulated_context: List[str] = Field(default_factory=list, description="All accumulated context")
    
    # Session management
    session_id: Optional[str] = Field(default=None, description="Session identifier")
    user_profile: Dict[str, Any] = Field(default_factory=dict, description="User preferences and history")
    
    # Performance tracking
    start_time: Optional[float] = Field(default=None, description="Workflow start time")
    tool_execution_times: Dict[str, float] = Field(default_factory=dict, description="Tool execution times")
    
    class Config:
        arbitrary_types_allowed = True
    
    def should_continue(self) -> bool:
        """Determine if the workflow should continue iterating."""
        return (
            self.iteration_count < self.max_iterations and
            self.last_quality_score < self.quality_threshold
        )
    
    def add_tool_usage(self, tool_name: str, execution_time: float = 0.0):
        """Record tool usage in the workflow."""
        self.tool_history.append(tool_name)
        self.current_tool = tool_name
        if execution_time > 0:
            self.tool_execution_times[tool_name] = execution_time
    
    def add_quality_grade(self, grade: QualityGrade):
        """Add a quality evaluation to the history."""
        self.quality_grades.append(grade)
        self.last_quality_score = grade.relevance_score
    
    def get_last_user_message(self) -> Optional[str]:
        """Extract the last user message from conversation history."""
        for message in reversed(self.messages):
            if hasattr(message, 'type') and message.type == 'human':
                return message.content
        return None
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the current state for logging/debugging."""
        return {
            "intent": self.current_intent,
            "iterations": self.iteration_count,
            "tools_used": self.tool_history,
            "quality_score": self.last_quality_score,
            "should_continue": self.should_continue(),
            "session_id": self.session_id
        }


class ToolExecutionState(BaseModel):
    """State for individual tool execution."""
    tool_name: str = Field(..., description="Name of the tool")
    input_data: Dict[str, Any] = Field(default_factory=dict, description="Input parameters")
    output_data: Optional[str] = Field(default=None, description="Tool output")
    execution_time: float = Field(default=0.0, description="Time taken to execute")
    success: bool = Field(default=False, description="Whether execution was successful")
    error_message: Optional[str] = Field(default=None, description="Error if execution failed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class WorkflowMetrics(BaseModel):
    """Metrics for workflow performance analysis."""
    total_queries: int = Field(default=0, description="Total queries processed")
    intent_accuracy: List[bool] = Field(default_factory=list, description="Intent classification accuracy")
    response_times: List[float] = Field(default_factory=list, description="Response times")
    iteration_stats: List[int] = Field(default_factory=list, description="Iterations per query")
    tool_usage: Dict[str, int] = Field(default_factory=dict, description="Tool usage frequency")
    quality_scores: List[float] = Field(default_factory=list, description="Quality scores")
    user_satisfaction: List[float] = Field(default_factory=list, description="User satisfaction scores")
    
    def get_accuracy_rate(self) -> float:
        """Calculate intent classification accuracy rate."""
        if not self.intent_accuracy:
            return 0.0
        return sum(self.intent_accuracy) / len(self.intent_accuracy)
    
    def get_average_response_time(self) -> float:
        """Calculate average response time."""
        if not self.response_times:
            return 0.0
        return sum(self.response_times) / len(self.response_times)
    
    def get_average_iterations(self) -> float:
        """Calculate average iterations per query."""
        if not self.iteration_stats:
            return 0.0
        return sum(self.iteration_stats) / len(self.iteration_stats)
    
    def get_most_used_tool(self) -> Optional[str]:
        """Get the most frequently used tool."""
        if not self.tool_usage:
            return None
        return max(self.tool_usage, key=self.tool_usage.get)
