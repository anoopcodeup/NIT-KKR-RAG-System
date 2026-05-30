# Development Workflow & Architecture

## Architecture Overview

```
┌─────────────────┐
│  React Frontend │  (Port 3000)
│   (Vite)        │
└────────┬────────┘
         │ HTTP/REST
         │
┌────────▼────────┐
│  FastAPI Backend│  (Port 8000)
│   (Python)      │
└────────┬────────┘
         │
┌────────▼────────┐
│   RAG System    │
│  (rag_system.py)│
└────────┬────────┘
         │
┌────────▼────────┐
│ Vector Store    │
│  (FAISS Index)  │
└─────────────────┘
```

## Component Breakdown

### Frontend (React + Vite)
- **Location**: `frontend/`
- **Tech Stack**: React 18, Vite, JavaScript
- **Key Components**:
  - `ChatInterface.jsx` - Main chat UI
  - `Message.jsx` - Individual message display with sources
  - `InputArea.jsx` - Query input with auto-resize
  - `StatsPanel.jsx` - System statistics sidebar
  - `Header.jsx` - App header

### Backend (FastAPI)
- **Location**: `backend/api.py`
- **Tech Stack**: FastAPI, Python
- **Endpoints**:
  - `GET /api/health` - Health check
  - `POST /api/query` - Query RAG system
  - `GET /api/stats` - Get system statistics

### RAG System
- **Location**: `rag_system.py`
- **Features**:
  - Vector similarity search
  - Reranking with CrossEncoder
  - Groq LLM integration
  - Template fallback

## Development Workflow

### 1. Initial Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies
cd frontend
npm install
```

### 2. Running Development Servers

**Terminal 1 - Backend:**
```bash
cd backend
python api.py
# Server runs on http://localhost:8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
# App runs on http://localhost:3000
```

### 3. Making Changes

#### Frontend Changes
- Edit files in `frontend/src/`
- Vite hot-reloads automatically
- No build step needed during development

#### Backend Changes
- Edit `backend/api.py`
- Uvicorn auto-reloads on file changes
- Test API at `http://localhost:8000/docs`

#### RAG System Changes
- Edit `rag_system.py`, `vector_embeddings.py`, etc.
- Restart backend server to apply changes

### 4. Testing

#### Test Backend API
```bash
# Health check
curl http://localhost:8000/api/health

# Query
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What are admission requirements?"}'

# Stats
curl http://localhost:8000/api/stats
```

#### Test Frontend
- Open `http://localhost:3000`
- Use browser DevTools for debugging
- Check Network tab for API calls

## Data Flow

### Query Flow

1. **User Input** → `InputArea.jsx`
2. **API Call** → `services/api.js` → `POST /api/query`
3. **Backend Processing** → `backend/api.py`
4. **RAG Processing** → `rag_system.py`
   - Vector search
   - Reranking (if enabled)
   - LLM generation
5. **Response** → Backend → Frontend
6. **Display** → `Message.jsx` with sources

### Stats Flow

1. **Component Mount** → `App.jsx`
2. **API Call** → `GET /api/stats`
3. **Backend** → `rag_system.get_system_stats()`
4. **Display** → `StatsPanel.jsx`

## File Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ChatInterface.jsx    # Main chat container
│   │   ├── Message.jsx          # Message display
│   │   ├── InputArea.jsx        # Input field
│   │   ├── StatsPanel.jsx       # Statistics panel
│   │   ├── Header.jsx           # App header
│   │   ├── MessageList.jsx      # Message list container
│   │   └── LoadingIndicator.jsx # Loading animation
│   ├── services/
│   │   └── api.js               # API service functions
│   ├── App.jsx                  # Main app component
│   ├── main.jsx                 # Entry point
│   └── index.css                # Global styles
├── package.json
├── vite.config.js
└── index.html

backend/
└── api.py                       # FastAPI server

Root/
├── rag_system.py                # RAG implementation
├── vector_embeddings.py         # Vector operations
├── config.py                    # Configuration
└── ...
```

## Styling Approach

- **CSS Variables**: Defined in `index.css` for theming
- **Component Styles**: Each component has its own CSS file
- **Responsive Design**: Mobile-first with media queries
- **Modern UI**: Clean, minimal design with shadows and borders

## API Integration

### Frontend → Backend
- Uses `fetch` API
- Proxy configured in `vite.config.js` for development
- Environment variable `VITE_API_BASE_URL` for production

### Error Handling
- Try-catch blocks in API service
- User-friendly error messages
- Loading states for better UX

## Best Practices

### Frontend
- ✅ Component-based architecture
- ✅ Separation of concerns (UI, services, styles)
- ✅ Reusable components
- ✅ Responsive design
- ✅ Loading states
- ✅ Error handling

### Backend
- ✅ RESTful API design
- ✅ Pydantic models for validation
- ✅ CORS configuration
- ✅ Error handling with HTTPException
- ✅ Logging for debugging

### Code Organization
- ✅ Clear file structure
- ✅ Consistent naming conventions
- ✅ Comments for complex logic
- ✅ Type hints (where applicable)

## Deployment Considerations

### Frontend
- Build: `npm run build`
- Output: `frontend/dist/`
- Serve with: nginx, Vercel, Netlify, etc.

### Backend
- Production server: `uvicorn backend.api:app --host 0.0.0.0 --port 8000`
- Or use: Gunicorn, Docker, etc.
- Environment variables for configuration

## Next Steps for Enhancement

1. **Authentication**: Add user authentication
2. **History**: Save chat history
3. **Export**: Export conversations
4. **Themes**: Dark mode support
5. **Analytics**: Track usage statistics
6. **Testing**: Add unit and integration tests
7. **CI/CD**: Set up continuous integration

