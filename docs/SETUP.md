# Setup Guide - NIT KKR Agentic RAG System

This guide will help you set up the complete agentic RAG system with intelligent query routing and multi-tool capabilities.

## Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher (for frontend)
- npm or yarn (for frontend)

## Step 1: Backend Setup

### 1.1 Install Python Dependencies

```bash
pip install -r requirements.txt
```

**Agentic System Dependencies Include:**
- `langchain>=1.2.18` - Core LangChain functionality
- `langchain-core>=1.4.0` - LangChain core components
- `langchain-groq>=1.1.2` - Groq LLM integration
- `langgraph>=1.1.10` - Agentic workflow orchestration
- `pydantic>=2.0.0` - Data validation and state management
- `numpy>=1.26.4` - Numerical computations
- `faiss-cpu>=1.7.0` - Vector similarity search
- `sentence-transformers>=2.2.2` - Text embeddings
- `groq>=0.4.1` - Groq API client
- `fastapi>=0.104.0` - API server
- `uvicorn[standard]>=0.24.0` - ASGI server

### 1.2 Set Up Groq API (Required for Agentic System)

1. Get your free API key from [Groq Console](https://console.groq.com/keys)
2. Run the setup script:
```bash
python setup_groq.py
```
Or manually create a `.env` file:
```
GROQ_API_KEY=your_api_key_here
GROQ_MODEL=llama-3.1-8b-instant
```

### 1.3 Optional: Set Up Web Search API

For real-time information queries (weather, news, etc.):
```bash
# Install Tavily API
pip install tavily-python

# Add to .env file
TAVILY_API_KEY=your_tavily_api_key
```

### 1.4 Prepare Data (If Not Already Done)

If you haven't scraped the website yet:

```bash
# Scrape the website
python main.py scrape

# Generate vector embeddings
python main.py embed
```

### 1.5 Start Agentic System

**Option A: Agentic RAG System (Recommended)**
```bash
python main.py rag
```

**Option B: Test Agentic System**
```bash
python test_intent_routing.py
```

**Option C: Custom Agentic Server**
```bash
python -c "
from agentic_system.workflows.agentic_rag import create_agentic_rag_workflow
from fastapi import FastAPI
import uvicorn

app = FastAPI()
workflow = create_agentic_rag_workflow()

@app.post('/agentic-query')
async def agentic_query(request):
    result = workflow.invoke({'query': request.query})
    return result

uvicorn.run(app, host='0.0.0.0', port=8000)
"
```

The API will be available at `http://localhost:8000`

You can also check the API documentation at `http://localhost:8000/docs`

## Step 2: Frontend Setup

### 2.1 Install Dependencies

```bash
cd frontend
npm install
```

### 2.2 Start Development Server

```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Step 3: Verify Setup

1. **Backend Health Check**: Visit `http://localhost:8000/api/health`
2. **Frontend**: Open `http://localhost:3000` in your browser
3. **Test Query**: Try asking a question like "What are the admission requirements?"

## Project Structure

```
FinalYearProject/
├── agentic_system/           # 🤖 Agentic RAG System
│   ├── agents/             # Intent router, quality evaluator
│   ├── tools/              # Vector store, web search, calculator
│   ├── workflows/           # Main workflow orchestration
│   └── utils/              # Prompts and utilities
├── backend/                 # 🌐 FastAPI backend server
│   └── api.py
├── frontend/                # ⚛️ React frontend
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   └── ...
│   └── package.json
├── vector_store/            # 📚 FAISS vector database
├── extracted_text/          # 📄 Scraped content
├── config.py
├── rag_system.py           # 🔄 Original RAG system
├── vector_embeddings.py     # 🔍 Vector embeddings
├── scraper.py             # 🕷️ Web scraper
├── main.py                # 🚀 Main entry point
├── requirements.txt        # 📦 Dependencies
├── SETUP.md              # 📋 Setup guide
└── AGENTIC_WORKFLOW_DIAGRAM.md  # 📊 Workflow documentation
```

## Step 3: Test Agentic System

### 3.1 Verify Agentic Capabilities

Test different query types to ensure proper routing:

```bash
# Test calculator functionality
python -c "
from agentic_system.workflows.agentic_rag import create_agentic_rag_workflow
workflow = create_agentic_rag_workflow()
result = workflow.invoke({'query': 'What is 2+2?'})
print('Intent:', result['intent'])
print('Tools:', result['tools_used'])
print('Response:', result['response'][:100])
"

# Test web search functionality
python -c "
from agentic_system.workflows.agentic_rag import create_agentic_rag_workflow
workflow = create_agentic_rag_workflow()
result = workflow.invoke({'query': 'How is weather in Kurukshetra?'})
print('Intent:', result['intent'])
print('Tools:', result['tools_used'])
print('Response:', result['response'][:100])
"

# Test university information
python -c "
from agentic_system.workflows.agentic_rag import create_agentic_rag_workflow
workflow = create_agentic_rag_workflow()
result = workflow.invoke({'query': 'What are CSE admission requirements?'})
print('Intent:', result['intent'])
print('Tools:', result['tools_used'])
print('Response:', result['response'][:100])
"
```

### 3.2 Expected Results

- **Calculator queries** → Intent: `calculation` → Tool: `calculator`
- **Weather queries** → Intent: `real_time_info` → Tool: `web_search`
- **University queries** → Intent: `university_info` → Tool: `vector_store`

## Step 4: Frontend Setup (Optional)

### 4.1 Install Dependencies

```bash
cd frontend
npm install
```

### 4.2 Start Development Server

```bash
cd frontend
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Development Workflow

### Running Both Systems

**Terminal 1 - Agentic Backend:**
```bash
python main.py rag
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Making Changes

- **Agentic System**: Changes in `agentic_system/` will auto-reload
- **Frontend**: Changes to React components will hot-reload automatically

## API Endpoints

### Agentic System Endpoints
- `POST /api/agentic-query` - Query the agentic RAG system
- `GET /api/workflow-stats` - Get workflow statistics

### Legacy RAG Endpoints
- `GET /api/health` - Health check
- `POST /api/query` - Query the original RAG system
- `GET /api/stats` - Get system statistics

## Troubleshooting

### Agentic System Issues

1. **Intent routing not working**: 
   - Check Groq API key in `.env` file
   - Verify LangGraph dependencies are installed
   - Check logs for classification errors

2. **Tool execution fails**:
   - Ensure required APIs are configured (Tavily for web search)
   - Check vector store is initialized: `python main.py stats`
   - Verify calculator tool imports

3. **Self-reflection loop not working**:
   - Check evaluator agent configuration
   - Verify quality thresholds in state management
   - Check iteration limits

### Backend Issues

1. **Port 8000 already in use**: Change the port or kill conflicting process
2. **Import errors**: Make sure you're in the project root directory
3. **Vector store not found**: Run `python main.py embed` first

### Frontend Issues

1. **Cannot connect to backend**: 
   - Ensure agentic system is running
   - Check CORS settings
   - Verify API endpoint URLs

## Production Build

### Agentic System

Deploy the agentic system:
```bash
# Using FastAPI
uvicorn main:app --host 0.0.0.0 --port 8000

# Or using custom server
python -c "
from agentic_system.workflows.agentic_rag import create_agentic_rag_workflow
from fastapi import FastAPI
import uvicorn

app = FastAPI()
workflow = create_agentic_rag_workflow()

@app.post('/agentic-query')
async def agentic_query(request):
    result = workflow.invoke({'query': request.query})
    return result

uvicorn.run(app, host='0.0.0.0', port=8000)
"
```

### Frontend

```bash
cd frontend
npm run build
npm install -g serve
serve -s dist
```

## Environment Variables

### Required (.env)
```bash
# LLM Configuration
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.1-8b-instant

# Optional: Web Search
TAVILY_API_KEY=your_tavily_api_key
```

### Frontend (.env)
```bash
VITE_API_BASE_URL=http://localhost:8000
```

## Agentic System Features

### 🤖 Intelligent Query Routing
- **Intent Classification**: Automatically identifies query type
- **Tool Selection**: Routes to appropriate tool based on intent
- **Multi-tool Support**: Can combine multiple tools for complex queries

### 🔧 Available Tools
- **Vector Store**: NIT KKR university information
- **Web Search**: Real-time information (weather, news, etc.)
- **Calculator**: Mathematical operations and fee calculations

### 🧠 Self-Reflection Loop
- **Quality Assessment**: Evaluates retrieved information quality
- **Query Rewriting**: Improves queries when quality is insufficient
- **Iterative Search**: Continues until quality threshold is met

### 📊 Response Metadata
- **Intent Information**: Shows classified intent
- **Tool History**: Lists tools used in response
- **Quality Scores**: Provides relevance and completeness metrics
- **Execution Time**: Tracks processing performance

## Next Steps

- **Custom Prompts**: Modify prompts in `agentic_system/utils/prompts.py`
- **Add Tools**: Implement new tools in `agentic_system/tools/`
- **Enhance Routing**: Improve intent classification accuracy
- **Deploy**: Set up production environment
- **Monitor**: Add logging and analytics

