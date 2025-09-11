# Donations

Donation Inventory — Setup & Run
A simple full-stack app: Flask + SQLite backend and Vite + React frontend.

### Prerequisites

- Python 3.11+
- Node.js 18+ (20+ recommended) and npm
- Git

### Backend (Flask)

From the repo root:
cd backend

### 1. Create and activate a virtual environment
python -m venv .venv

macOS/Linux
source .venv/bin/activate

Windows (PowerShell)
.venv\Scripts\Activate.ps1

### 2. Install dependencies
pip install -r requirements.txt

### 3. Run Flask
flask run

✅ The project includes a .flaskenv file, so you don’t need to manually export environment variables — Flask will auto-load them.
By default, the backend runs at http://127.0.0.1:5000

### Frontend (Vite + React)
In a new terminal (leave Flask running):
cd frontend

### 1. Install dependencies
npm install

### 2. Run the dev server
npm run dev

The frontend runs at http://localhost:5173
> API requests to `/api` are automatically proxied to the Flask backend
> (`http://127.0.0.1:5000`) via the Vite config in `vite.config.js`.