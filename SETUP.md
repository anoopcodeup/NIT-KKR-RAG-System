# Setup Guide - NIT KKR RAG System with Frontend

This guide will help you set up the complete system with React frontend and FastAPI backend.

## Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- npm or yarn

## Step 1: Backend Setup

### 1.1 Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 1.2 Set Up Groq API (Optional but Recommended)

1. Get your free API key from [Groq Console](https://console.groq.com/keys)
2. Run the setup script:
```bash
python setup_groq.py
```
Or manually create a `.env` file:
```
GROQ_API_KEY=your_api_key_here
```

### 1.3 Prepare Data (If Not Already Done)

If you haven't scraped the website yet:

```bash
# Scrape the website
python main.py scrape

# Generate vector embeddings
python main.py embed
```

### 1.4 Start Backend Server

```bash
cd backend
python api.py
```

Or using uvicorn directly:
```bash
uvicorn backend.api:app --reload --host 0.0.0.0 --port 8000
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
├── backend/
│   └── api.py              # FastAPI backend server
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API service layer
│   │   └── ...
│   └── package.json
├── config.py
├── rag_system.py
├── vector_embeddings.py
├── scraper.py
├── main.py
└── requirements.txt
```

## Development Workflow

### Running Both Servers

**Terminal 1 - Backend:**
```bash
cd backend
python api.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Making Changes

- **Backend**: Changes to `backend/api.py` will auto-reload with uvicorn
- **Frontend**: Changes to React components will hot-reload automatically

## API Endpoints

- `GET /` - API information
- `GET /api/health` - Health check
- `POST /api/query` - Query the RAG system
- `GET /api/stats` - Get system statistics

## Troubleshooting

### Backend Issues

1. **Port 8000 already in use**: Change the port in `backend/api.py` or kill the process using port 8000
2. **Vector store not found**: Run `python main.py embed` first
3. **Import errors**: Make sure you're in the project root directory

### Frontend Issues

1. **Cannot connect to backend**: 
   - Ensure backend is running on port 8000
   - Check CORS settings in `backend/api.py`
   - Verify `VITE_API_BASE_URL` in `.env` file

2. **npm install fails**: 
   - Try deleting `node_modules` and `package-lock.json`
   - Run `npm install` again

3. **Build errors**: 
   - Check Node.js version (should be 16+)
   - Clear cache: `npm cache clean --force`

## Production Build

### Backend

The backend can be deployed using:
```bash
uvicorn backend.api:app --host 0.0.0.0 --port 8000
```

### Frontend

Build the frontend:
```bash
cd frontend
npm run build
```

Serve the `dist` folder using a web server like nginx or serve it with:
```bash
npm install -g serve
serve -s dist
```

## Environment Variables

### Backend (.env)
```
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.1-8b-instant
```

### Frontend (.env)
```
VITE_API_BASE_URL=http://localhost:8000
```

## Next Steps

- Customize the UI in `frontend/src/components/`
- Add more API endpoints in `backend/api.py`
- Enhance the RAG system in `rag_system.py`
- Add authentication if needed
- Deploy to production

