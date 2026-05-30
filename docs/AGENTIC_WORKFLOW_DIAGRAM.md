# Agentic RAG System - Complete Workflow Documentation

## 🚀 System Startup Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    SYSTEM STARTUP                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  1. Environment Initialization                              │
│  ├─ Load .env file (API keys, config)                       │
│  ├─ Set up logging configuration                            │
│  └─ Initialize virtual environment                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Dependency Loading                                      │
│  ├─ Import LangGraph, LangChain, Pydantic                   │
│  ├─ Load existing RAG system modules                        │
│  └─ Initialize vector store (FAISS)                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Agentic System Initialization                           │
│  ├─ Create RouterAgent (intent classification)              │
│  ├─ Create EvaluatorAgent (quality assessment)              │
│  ├─ Initialize Tools (VectorStore, WebSearch, Calculator)   │
│  └─ Build LangGraph workflow with all nodes                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  4. Service Ready State                                     │
│  ├─ FastAPI server starts                                   │
│  ├─ Frontend connects to backend                            │
│  └─ System ready to handle user queries                     │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 User Query Processing Workflow

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Query    │───▶│   FastAPI        │───▶│  AgenticRAG    │
│   (Frontend)    │    │   Endpoint       │    │  Workflow       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    LANGGRAPH WORKFLOW                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  START → Router Node                                        │
│  Purpose: Classify query intent and route to appropriate    │
│  tool                                                       │
│                                                             │
│  Files Involved:                                            │
│  ├─ agentic_system/workflows/agentic_rag.py                 │
│  └─ agentic_system/agents/router_agent.py                   │
│                                                             │
│  Process:                                                   │
│  1. Receive AgenticState with user query                   │
│  2. Call RouterAgent.classify_intent()                     │
│  3. Determine which tool to use based on intent            │
│  4. Update state with routing information                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Conditional Edge: Should Use Tools?                        │
│                                                             │
│  Decision Logic:                                            │
│  ├─ If no tool selected → Direct Response                   │
│  ├─ If tool available and no context → Use Tools            │
│  └─ If context exists and iterations > 0 → Direct Response  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Tools Node (LangGraph ToolNode)                           │
│  Purpose: Execute appropriate tool based on routing         │
│                                                             │
│  Files Involved:                                            │
│  ├─ agentic_system/tools/vector_store_tool.py              │
│  ├─ agentic_system/tools/web_search_tool.py                │
│  └─ agentic_system/tools/calculator_tool.py                 │
│                                                             │
│  Tool Selection:                                            │
│  ├─ UNIVERSITY_INFO → vector_store_tool.py                 │
│  ├─ REAL_TIME_INFO → web_search_tool.py                     │
│  ├─ CALCULATION → calculator_tool.py                        │
│  └─ COMPARISON → multi_tool execution                       │
│                                                             │
│  Process:                                                   │
│  1. Execute selected tool                                   │
│  2. Get tool response                                       │
│  3. Update state.retrieved_context                          │
│  4. Add tool to state.tool_history                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Evaluator Node                                             │
│  Purpose: Assess quality of retrieved information          │
│                                                             │
│  Files Involved:                                            │
│  └─ agentic_system/agents/evaluator_agent.py               │
│                                                             │
│  Process:                                                   │
│  1. Get query and context from state                        │
│  2. Call EvaluatorAgent.evaluate_retrieved_info()          │
│  3. Get QualityGrade with scores                           │
│  4. Add grade to state.quality_grades                      │
│  5. Update state.iteration_count if needed                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Conditional Edge: Should Continue Search?                 │
│                                                             │
│  Decision Logic:                                            │
│  ├─ If quality scores < 0.7 → Continue (Rewrite Query)     │
│  ├─ If should_continue = "yes" → Continue                  │
│  ├─ If iteration_count < max_iterations → Continue          │
│  └─ Else → Generate Response                                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Rewriter Node (Self-Reflection Loop)                       │
│  Purpose: Improve query based on quality feedback          │
│                                                             │
│  Files Involved:                                            │
│  └─ agentic_system/workflows/agentic_rag.py                │
│                                                             │
│  Process:                                                   │
│  1. Get original query and quality feedback                │
│  2. Generate improved query using heuristics               │
│  3. Update state.messages with rewritten query             │
│  4. Route back to Router Node                               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Generator Node                                             │
│  Purpose: Create final response for user                   │
│                                                             │
│  Files Involved:                                            │
│  └─ agentic_system/workflows/agentic_rag.py                │
│                                                             │
│  Process:                                                   │
│  1. Get user query and accumulated context                 │
│  2. Format response with metadata                           │
│  3. Add AI message to state.messages                       │
│  4. Calculate execution time                               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  END → Return Response                                      │
│  Purpose: Send final response back to user                 │
│                                                             │
│  Output Format:                                             │
│  ├─ response: Final answer text                            │
│  ├─ intent: Classified query intent                        │
│  ├─ tools_used: List of tools executed                     │
│  ├─ iterations: Number of search iterations               │
│  ├─ quality_score: Final quality assessment                │
│  └─ execution_time: Total processing time                  │
└─────────────────────────────────────────────────────────────┘
```

## 📁 File-by-File Interaction Flow

### **Entry Point:** `main.py`
```python
# When system starts
if __name__ == "__main__":
    # 1. Initialize FastAPI app
    app = create_app()
    
    # 2. Start server
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### **API Layer:** `app.py` (FastAPI endpoints)
```python
# When user sends query via frontend
@app.post("/api/agentic-query")
async def agentic_query(request: QueryRequest):
    # 1. Create AgenticRAGWorkflow instance
    workflow = create_agentic_rag_workflow()
    
    # 2. Invoke workflow with user query
    result = workflow.invoke({"query": request.query})
    
    # 3. Return response to frontend
    return result
```

### **Workflow Orchestration:** `agentic_system/workflows/agentic_rag.py`
```python
# Main workflow execution
class AgenticRAGWorkflow:
    def invoke(self, input_data):
        # 1. Create initial AgenticState
        state = AgenticState(messages=[HumanMessage(content=query)])
        
        # 2. Execute LangGraph workflow
        result = self.graph.invoke(state)
        
        # 3. Extract final response
        return format_response(result)
```

### **State Management:** `agentic_system/workflows/state_management.py`
```python
# State flows through all nodes
class AgenticState:
    # 1. Router updates: current_intent, current_tool
    # 2. Tools update: retrieved_context, tool_history  
    # 3. Evaluator updates: quality_grades, iteration_count
    # 4. Generator updates: final AI message
```

### **Agent Processing:** `agentic_system/agents/`
```python
# Router Agent - Intent Classification
router_agent.py:
    classify_intent() → IntentClassification → update state

# Evaluator Agent - Quality Assessment  
evaluator_agent.py:
    evaluate_retrieved_info() → QualityGrade → update state
```

### **Tool Execution:** `agentic_system/tools/`
```python
# Vector Store Tool - University information
vector_store_tool.py:
    search_university_info() → context → update state

# Web Search Tool - Real-time information
web_search_tool.py:
    search_web() → context → update state

# Calculator Tool - Mathematical operations
calculator_tool.py:
    calculate() → result → update state
```

## 🔄 Complete Request Flow Example

**User Query:** "What are CSE admission requirements and total fees for 4 years?"

1. **Frontend → Backend**: HTTP POST to `/api/agentic-query`
2. **FastAPI → AgenticWorkflow**: Create workflow instance
3. **Router Node**:
   - Classify intent: `UNIVERSITY_INFO + CALCULATION`
   - Route to: `vector_store_tool` + `calculator_tool`
4. **Tools Node**:
   - Execute `search_university_info()` → CSE requirements
   - Execute `calculate()` → 4-year fee calculation
5. **Evaluator Node**:
   - Assess quality of retrieved information
   - If quality < 0.7 → Continue search
   - If quality ≥ 0.7 → Generate response
6. **Generator Node**:
   - Format response with admission requirements
   - Include fee calculation results
   - Add metadata (tools used, iterations, quality score)
7. **Backend → Frontend**: JSON response with all information

## 🎯 Key Decision Points

### **Intent Classification Decisions**
```python
# Router Agent determines:
UNIVERSITY_INFO → vector_store_tool.py
REAL_TIME_INFO → web_search_tool.py  
CALCULATION → calculator_tool.py
COMPARISON → multi_tool_execution
```

### **Quality Evaluation Decisions**
```python
# Evaluator Agent determines:
relevance_score < 0.7 → Rewrite query
completeness_score < 0.7 → Continue search
freshness_score < 0.7 → Try web search
```

### **Self-Reflection Loop**
```python
# If quality insufficient:
1. Rewriter Node improves query
2. Router Node re-classifies improved query  
3. Tools Node executes with better query
4. Loop continues until quality acceptable
```

## 📊 System State Evolution

```
Initial State:
├─ messages: [HumanMessage(query)]
├─ current_intent: None
├─ current_tool: None
├─ retrieved_context: ""
├─ quality_grades: []
├─ iteration_count: 0
└─ tool_history: []

After Router:
├─ current_intent: UNIVERSITY_INFO
├─ current_tool: vector_store
└─ intent_classification: IntentClassification(...)

After Tools:
├─ retrieved_context: "CSE admission requirements..."
├─ tool_history: ["vector_store"]
└─ tool_execution_times: [1.2]

After Evaluator:
├─ quality_grades: [QualityGrade(relevance=0.8, ...)]
├─ iteration_count: 1
└─ last_quality_score: 0.8

After Generator:
├─ messages: [..., AIMessage(response)]
└─ execution_time: 2.5
```

This workflow ensures intelligent query processing, self-correction, and optimal tool selection for every user request!
