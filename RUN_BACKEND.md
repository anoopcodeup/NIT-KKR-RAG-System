# Running FastAPI Backend in Virtual Environment

## 🐍 Setup Virtual Environment (Windows)

### Step 1: Create Virtual Environment
```bash
# From project root directory
python -m venv venv
```

### Step 2: Activate Virtual Environment
```bash
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Windows Command Prompt (CMD)
venv\Scripts\activate.bat

# If PowerShell execution policy error, run this first:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Setup Groq API (Optional)
```bash
python setup_groq.py
```

### Step 5: Prepare Data (If Not Already Done)
```bash
# Scrape the website
python main.py scrape

# Generate vector embeddings
python main.py embed
```

### Step 6: Run FastAPI Backend
```bash
cd backend
python api.py
```

Or from project root:
```bash
python backend/api.py
```

---

## 📋 Complete Command Sequence

```bash
# 1. Create venv
python -m venv venv

# 2. Activate venv (PowerShell)
.\venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup Groq (optional)
python setup_groq.py

# 5. Prepare data (if needed)
python main.py embed

# 6. Run backend
cd backend
python api.py
```

---

## ✅ Verify Setup

After running, you should see:
- Server running on: `http://localhost:8000`
- API docs at: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/api/health`

---

## 🔄 Daily Usage

Once venv is set up, just activate and run:

```bash
# Activate venv
.\venv\Scripts\Activate.ps1

# Run backend
cd backend
python api.py
```

---

## 🛑 Deactivate Virtual Environment

When done:
```bash
deactivate
```

---

## 🐛 Troubleshooting

### PowerShell Execution Policy Error
```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Port Already in Use
```bash
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace <PID> with actual PID)
taskkill /PID <PID> /F
```

### Virtual Environment Not Found
Make sure you're in the project root directory when creating venv.

