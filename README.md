#  Smart Personal CFO

An **AI-powered financial advisor** that transforms **raw receipts into actionable insights** using **FastAPI, Next.js, and Google Gemini OCR**.

---

##  Tech Stack

### Frontend
- **Next.js 16** (App Router)
- **Tailwind CSS v4**
- **Lucide React**
- **Recharts**

###  Backend
- **FastAPI** (Python 3.13)
- **Motor** (Async MongoDB)
- **Pydantic v2**

###  AI / ML
- **OCR Engine**
- **Gemini-powered LLM Parsing**

###  Security
- **JWT (JSON Web Tokens)**
- **Bcrypt Password Hashing**
- **Protected Routes**

---

##  Project Structure

```plaintext
smart-personal-cfo/
├── frontend/                  # Next.js Application
│   ├── app/                   # Dashboard & Auth Routes
│   ├── components/            # Transaction Modal & UI Kits
│   └── lib/                   # AuthContext & API Client
│
└── backend/                   # FastAPI Application
    ├── app/
    │   ├── routers/           # Auth, Transactions, Analytics
    │   ├── services/          # OCR & AI Parsing Logic
    │   └── db/                # MongoDB Connection
    │
    └── uploads/               # Secure receipt image storage
```

---

##  Quick Start

### 1️⃣ Backend Setup

```bash
cd backend
python -m venv venv
source venv/Scripts/activate   # Windows
pip install -r requirements.txt
```

###  Environment Variables

Create a `.env` file inside `/backend`:

```env
MONGO_USER=your_user
MONGO_PASSWORD=your_password
MONGO_CLUSTER=your_cluster
DATABASE_NAME=smart_cfo
SECRET_KEY=your_random_hex_key
ALGORITHM=HS256
```

###  Run Backend

```bash
uvicorn app.main:app --reload
```

---

### 2️⃣ Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Visit:

```bash
http://localhost:3000
```

to start managing your finances 💸

---

##  Roadmap & Progress

###  Completed
- [x] **Phase 1–4:** Core OCR Engine + MongoDB Integration
- [x] **Phase 5:** High-performance Analytics Engine (`$group` aggregations)
- [x] **Phase 6:** JWT Authentication + Protected Routes
- [x] **Phase 7:** AI Scanner Modal + Real-time Dashboard Sync

###  Upcoming
- [ ] **Phase 8:** AI Budgeting Advisor (Chat Interface)
- [ ] **Phase 9:** Export to CSV/PDF for tax purposes
- [ ] **Phase 10:** Multi-currency Support + Cloud Deployment