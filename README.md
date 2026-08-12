# AryaCrypt

AryaCrypt is an enterprise-grade web application for secure file encryption utilizing the novel Aryabhata-based cryptographic framework. This project features a strict separation of concerns with a modern React frontend and a robust Python backend.

## Prerequisites

Before you begin, ensure you have the following installed on your machine:
*   **Node.js** (v18 or higher)
*   **npm** (Node Package Manager)
*   **Python** (v3.9 or higher)
*   **PostgreSQL** (Running locally or accessible via network)

---

## 🛠️ Backend Setup & Installation

The backend is built with Python (FastAPI).

### 1. Navigate to the backend directory
```bash
cd backend
```

### 2. Create and activate a Virtual Environment
**For Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```
**For macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Variables
1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and configure your database credentials and secret keys.

### 5. Run Database Migrations (Alembic)
Ensure your PostgreSQL database is running, then apply migrations:
```bash
alembic upgrade head
```

### 6. Start the Backend Server
Run the FastAPI development server:
```bash
uvicorn app.main:app --reload
```
The backend API will now be running at `http://localhost:8000`.

---

## 💻 Frontend Setup & Installation

The frontend is a React Application built with Vite and TypeScript.

### 1. Navigate to the frontend directory
Open a **new terminal window** (keep the backend running in the other) and run:
```bash
cd frontend
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Start the Development Server
```bash
npm run dev
```
The frontend application will now be running, typically at `http://localhost:5173`.

---

## Usage

1. Open your browser and navigate to the frontend URL (`http://localhost:5173`).
2. Create an account or log in.
3. Use the interface to securely upload, encrypt, and decrypt files!
