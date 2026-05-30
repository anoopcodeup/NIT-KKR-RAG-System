# Frontend Overview - NIT KKR RAG System

## 📋 Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Technology Stack](#technology-stack)
3. [Project Structure](#project-structure)
4. [Component Breakdown](#component-breakdown)
5. [State Management](#state-management)
6. [API Integration](#api-integration)
7. [Styling & Theming](#styling--theming)
8. [User Experience Features](#user-experience-features)
9. [Development Setup](#development-setup)

---

## 🏗️ Architecture Overview

The frontend is a **React-based Single Page Application (SPA)** built with **Vite** as the build tool. It follows a **component-based architecture** with clear separation of concerns:

```
┌─────────────────────────────────────┐
│           App.jsx (Root)            │
│  - State Management (Dark Mode)     │
│  - Stats Fetching                   │
└──────────────┬──────────────────────┘
               │
       ┌───────┴────────┐
       │                │
┌──────▼──────┐  ┌──────▼──────┐
│   Header    │  │ App Container│
│  Component  │  └──────┬───────┘
└─────────────┘         │
                 ┌──────┴──────┐
                 │             │
          ┌──────▼──────┐ ┌───▼────────┐
          │   Chat      │ │   Stats    │
          │ Interface   │ │   Panel    │
          └─────────────┘ └────────────┘
```

---

## 🛠️ Technology Stack

### Core Technologies
- **React 18.2.0** - UI library
- **Vite 5.0.8** - Build tool and dev server
- **JavaScript (ES6+)** - Programming language

### Dependencies
- **react** & **react-dom** - Core React libraries
- **axios** (installed but using native fetch) - HTTP client (available for future use)

### Development Tools
- **@vitejs/plugin-react** - Vite React plugin
- **@types/react** & **@types/react-dom** - TypeScript definitions

---

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── ChatInterface.jsx/css
│   │   ├── Header.jsx/css
│   │   ├── StatsPanel.jsx/css
│   │   ├── InputArea.jsx/css
│   │   ├── Message.jsx/css
│   │   ├── MessageList.jsx/css
│   │   └── LoadingIndicator.jsx/css
│   ├── services/            # API service layer
│   │   └── api.js
│   ├── App.jsx              # Root component
│   ├── App.css              # Main app styles
│   ├── main.jsx             # Entry point
│   └── index.css            # Global styles
├── package.json
├── vite.config.js           # Vite configuration
└── index.html               # HTML template
```

---

## 🧩 Component Breakdown

### 1. **App.jsx** (Root Component)
**Purpose**: Main application container and state management

**Responsibilities**:
- Manages dark mode state
- Fetches system statistics on mount
- Provides layout structure (Header + Main Content + Sidebar)
- Passes props to child components

**State**:
- `stats` - System statistics data
- `loading` - Loading state for stats
- `darkMode` - Theme toggle state

**Key Features**:
- Auto-fetches stats on component mount
- Conditional dark mode class application
- Error handling for stats fetching

---

### 2. **Header.jsx** (Navigation Header)
**Purpose**: Application header with branding and controls

**Features**:
- Application title and subtitle
- "Powered by RAG" status badge with animated dot
- Dark/Light mode toggle button (🌙/☀️)
- Responsive design

**Props**:
- `darkMode` - Current theme state
- `setDarkMode` - Theme toggle function

**Styling**:
- Gradient background in light mode
- Backdrop blur effect
- Smooth transitions

---

### 3. **ChatInterface.jsx** (Main Chat Component)
**Purpose**: Core chat functionality and message management

**State**:
- `messages` - Array of chat messages
- `loading` - Loading state during API calls
- `messagesEndRef` - Reference for auto-scrolling

**Features**:
- **Welcome Screen**: 
  - Animated chatbot icon
  - Title and subtitle
  - Clickable suggestion chips (3 pre-defined questions)
  - Only shown when no messages exist

- **Message Display**:
  - Renders MessageList component
  - Auto-scrolls to bottom on new messages
  - Shows LoadingIndicator during API calls

- **Message Handling**:
  - Sends user messages to API
  - Displays bot responses with sources
  - Error handling with user-friendly messages
  - Timestamp tracking

**API Integration**:
- Uses `queryRAG()` from `services/api.js`
- Default `k=5` for document retrieval

---

### 4. **MessageList.jsx** (Message Container)
**Purpose**: Renders list of messages

**Features**:
- Maps through messages array
- Renders individual Message components
- Shows LoadingIndicator when loading
- Simple container with gap spacing

**Props**:
- `messages` - Array of message objects
- `loading` - Boolean loading state

---

### 5. **Message.jsx** (Individual Message)
**Purpose**: Displays a single message with sources

**State**:
- `showSources` - Toggle for source visibility

**Features**:
- **Message Types**:
  - User messages (right-aligned, blue background)
  - Bot messages (left-aligned, gray background)
  - Error messages (special styling)

- **Avatar Display**:
  - 🤖 for bot messages
  - 👤 for user messages

- **Source Display**:
  - Collapsible source list
  - Shows source count
  - Displays: title, URL, relevance/rerank score, content preview
  - Clickable URLs (opens in new tab)

- **Timestamp**: Shows time in HH:MM format

**Props**:
- `message` - Message object with:
  - `id`, `type`, `content`, `timestamp`
  - `sources` (optional array)
  - `error` (optional boolean)

---

### 6. **InputArea.jsx** (Message Input)
**Purpose**: Text input for user queries

**State**:
- `input` - Current input text
- `textareaRef` - Reference for auto-resize

**Features**:
- **Auto-resizing Textarea**:
  - Grows with content
  - Minimum 1 row, expands as needed

- **Keyboard Shortcuts**:
  - Enter: Submit message
  - Shift+Enter: New line

- **Send Button**:
  - Shows ⏳ when loading
  - Shows ➤ when ready
  - Disabled when input is empty or loading

- **User Hints**: Shows keyboard shortcut instructions

**Props**:
- `onSendMessage` - Callback function
- `loading` - Disables input during API calls

---

### 7. **StatsPanel.jsx** (Statistics Sidebar)
**Purpose**: Displays system statistics

**Features**:
- **Statistics Display**:
  - Total Chunks
  - Documents count
  - Total Words
  - Average Chunk Length

- **Model Information**:
  - Embedding Model name
  - Embedding dimension

- **System Status**:
  - Groq LLM status (✓ Enabled / ✗ Disabled)
  - Groq Model name (if enabled)
  - Reranker status (✓ Enabled / ⚠ Disabled)

- **Refresh Button**: Manual stats refresh

**States**:
- Loading state
- Error state
- Data display state

**Props**:
- `stats` - Statistics object
- `loading` - Loading state
- `onRefresh` - Refresh callback

---

### 8. **LoadingIndicator.jsx** (Loading Animation)
**Purpose**: Visual feedback during API calls

**Features**:
- Animated three-dot loading indicator
- Bot avatar (🤖)
- Matches message bubble styling
- Smooth animation

---

## 🔄 State Management

### Local Component State
- Each component manages its own local state using React hooks
- No global state management library (Redux, Zustand, etc.)

### State Flow
```
App.jsx
  ├── darkMode → Header (theme toggle)
  ├── stats → StatsPanel (display)
  └── fetchStats → API call

ChatInterface.jsx
  ├── messages → MessageList → Message (display)
  ├── loading → LoadingIndicator (show/hide)
  └── handleSendMessage → API call → update messages
```

### Props Drilling
- Minimal props drilling
- State passed down from parent to children
- Callbacks passed up for user interactions

---

## 🌐 API Integration

### Service Layer (`services/api.js`)

**Base URL Configuration**:
- Uses environment variable `VITE_API_BASE_URL`
- Falls back to `http://localhost:8000` in development
- Vite proxy configured for `/api` routes

**API Functions**:

1. **`queryRAG(query, k=5)`**
   - POST `/api/query`
   - Sends user query to backend
   - Returns: `{ query, response, sources, num_sources }`
   - Error handling with user-friendly messages

2. **`getStats()`**
   - GET `/api/stats`
   - Fetches system statistics
   - Returns: Statistics object

3. **`checkHealth()`**
   - GET `/api/health`
   - Checks API health status
   - Available but not currently used in UI

**Error Handling**:
- Try-catch blocks in all API functions
- Console error logging
- User-friendly error messages in UI

**Vite Proxy Configuration**:
```javascript
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
  }
}
```

---

## 🎨 Styling & Theming

### CSS Architecture
- **Component-scoped CSS**: Each component has its own CSS file
- **Global Styles**: `index.css` for base styles
- **App-level Styles**: `App.css` for layout and theme variables

### Theme System

**CSS Variables** (Light Mode):
```css
--surface: #ffffff
--background: #f7f7f7
--text-primary: #111827
--text-secondary: #6b7280
--primary-color: #4f46e5
--border: #e5e7eb
```

**Dark Mode**:
- Toggle via `darkMode` state in App.jsx
- CSS variables overridden in `.app.dark` selector
- Smooth transitions between themes

### Design Features

**Colors**:
- Primary: Indigo/Purple (#4f46e5)
- Success: Green (#10b981)
- Error: Red (#ef4444)
- Neutral grays for backgrounds

**Typography**:
- System font stack (Inter, Segoe UI, etc.)
- Responsive font sizes
- Clear hierarchy

**Layout**:
- Flexbox-based layout
- Responsive design (mobile-first)
- Max-width container (1400px)
- Proper spacing and gaps

**Visual Effects**:
- Subtle gradients in header and background
- Box shadows for depth
- Smooth transitions and animations
- Backdrop blur effects

---

## ✨ User Experience Features

### 1. **Welcome Screen**
- Clean, centered layout
- Animated chatbot icon
- Clickable suggestion chips for quick start
- Only appears when chat is empty

### 2. **Message Display**
- Clear visual distinction between user and bot messages
- User messages: Right-aligned, blue background
- Bot messages: Left-aligned, gray background
- Timestamps for all messages
- Source citations with expandable details

### 3. **Input Experience**
- Auto-resizing textarea
- Keyboard shortcuts (Enter to send)
- Loading states prevent double-submission
- Clear placeholder text

### 4. **Loading States**
- Animated loading indicator
- Disabled inputs during API calls
- Visual feedback throughout

### 5. **Error Handling**
- User-friendly error messages
- Graceful degradation
- Console logging for debugging

### 6. **Responsive Design**
- Mobile-friendly layout
- Adaptive spacing
- Touch-friendly buttons
- Readable on all screen sizes

### 7. **Dark Mode**
- System-wide theme toggle
- Smooth transitions
- Consistent color scheme
- Icon-based toggle (🌙/☀️)

### 8. **Accessibility**
- Semantic HTML
- ARIA labels where needed
- Keyboard navigation support
- Color contrast compliance

---

## 🚀 Development Setup

### Prerequisites
- Node.js 16+ 
- npm or yarn

### Installation
```bash
cd frontend
npm install
```

### Development Server
```bash
npm run dev
```
- Runs on `http://localhost:3000` (or next available port)
- Hot Module Replacement (HMR) enabled
- API proxy configured for `/api` routes

### Build for Production
```bash
npm run build
```
- Outputs to `dist/` directory
- Optimized and minified
- Ready for deployment

### Preview Production Build
```bash
npm run preview
```

### Environment Variables
Create `.env` file in `frontend/` directory:
```
VITE_API_BASE_URL=http://localhost:8000
```

---

## 📊 Data Flow

### Query Flow
```
User Input (InputArea)
  ↓
handleSendMessage (ChatInterface)
  ↓
queryRAG() (api.js)
  ↓
POST /api/query (Backend)
  ↓
Response with answer + sources
  ↓
Update messages state
  ↓
Render Message components
```

### Stats Flow
```
App Component Mount
  ↓
fetchStats()
  ↓
GET /api/stats (Backend)
  ↓
Update stats state
  ↓
Pass to StatsPanel
  ↓
Display statistics
```

---

## 🔧 Key Features Implementation

### Auto-scrolling
- Uses `useRef` and `scrollIntoView`
- Smooth scrolling behavior
- Triggers on message array changes

### Message Formatting
- Markdown support (via message content)
- Source links are clickable
- Timestamps formatted with `toLocaleTimeString`

### Source Display
- Collapsible/expandable list
- Shows relevance scores
- Displays content previews
- Clickable URLs

### Theme Persistence
- Currently session-based (resets on refresh)
- Could be extended with localStorage

---

## 🎯 Component Communication

```
App.jsx
  ├── Header
  │     └── Receives: darkMode, setDarkMode
  │
  └── App Container
        ├── ChatInterface
        │     ├── MessageList
        │     │     └── Message (multiple)
        │     └── InputArea
        │           └── Calls: handleSendMessage
        │
        └── StatsPanel
              └── Receives: stats, loading, onRefresh
```

---

## 📝 Code Quality

### Best Practices
- ✅ Component-based architecture
- ✅ Separation of concerns
- ✅ Reusable components
- ✅ Error handling
- ✅ Loading states
- ✅ Responsive design
- ✅ Clean code structure

### Areas for Enhancement
- State management library (if complexity grows)
- TypeScript migration (for type safety)
- Unit tests (Jest + React Testing Library)
- E2E tests (Playwright/Cypress)
- Performance optimization (React.memo, useMemo)
- LocalStorage for theme persistence
- Message history persistence

---

## 🔐 Security Considerations

- API calls use HTTPS in production
- Input sanitization handled by backend
- XSS protection via React's built-in escaping
- CORS configured on backend
- No sensitive data stored in frontend

---

## 📱 Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- ES6+ features used
- CSS Grid and Flexbox
- Fetch API

---

## 🎨 Design Philosophy

1. **Simplicity**: Clean, uncluttered interface
2. **Clarity**: Clear visual hierarchy
3. **Feedback**: Loading states and error messages
4. **Accessibility**: Keyboard navigation and screen reader support
5. **Responsiveness**: Works on all device sizes
6. **Performance**: Fast load times and smooth interactions

---

This frontend provides a modern, user-friendly interface for interacting with the NIT KKR RAG system, with a focus on clean design, smooth user experience, and reliable functionality.

