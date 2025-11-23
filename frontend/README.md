# NIT KKR RAG Frontend

Modern React frontend for the NIT Kurukshetra RAG System, built with Vite.

## Features

- 🎨 Modern, responsive UI design
- 💬 Interactive chat interface
- 📊 Real-time system statistics
- 🔍 Source citations with relevance scores
- ⚡ Fast development with Vite
- 📱 Mobile-friendly design

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## Build

To build for production:
```bash
npm run build
```

The built files will be in the `dist` directory.

## Environment Variables

Create a `.env` file (optional):
```
VITE_API_BASE_URL=http://localhost:8000
```

If not set, it defaults to `http://localhost:8000`.

## Project Structure

```
frontend/
├── src/
│   ├── components/      # React components
│   │   ├── ChatInterface.jsx
│   │   ├── Header.jsx
│   │   ├── Message.jsx
│   │   ├── InputArea.jsx
│   │   └── StatsPanel.jsx
│   ├── services/        # API services
│   │   └── api.js
│   ├── App.jsx          # Main app component
│   ├── main.jsx         # Entry point
│   └── index.css        # Global styles
├── package.json
└── vite.config.js
```

