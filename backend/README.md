# ClariFi AI Backend

A RAG-powered financial advisory system built with FastAPI, MongoDB Atlas, ChromaDB, and Google Gemini.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Frontend (React/Vite)                        │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        FastAPI Backend                              │
├─────────────────────────────────────────────────────────────────────┤
│  Routes: /auth  /finance  /chat  /analytics  /market                │
├─────────────────────────────────────────────────────────────────────┤
│  Services Layer                                                      │
│  ┌───────────┐ ┌───────────────┐ ┌──────────────┐ ┌──────────────┐  │
│  │   Auth    │ │   Finance     │ │     Chat     │ │  Analytics   │  │
│  │  Service  │ │   Service     │ │   Service    │ │   Service    │  │
│  └───────────┘ └───────────────┘ └──────────────┘ └──────────────┘  │
│                        │                                             │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                    Financial Rules Engine                      │  │
│  │         (Deterministic Calculations - NO LLM)                  │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ┌───────────────────┐              ┌────────────────────────────┐  │
│  │   RAG Engine      │              │   Gemini LLM Service       │  │
│  │   (ChromaDB)      │──────────────│   (Explanation Only)       │  │
│  └───────────────────┘              └────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                    │                              │
                    ▼                              ▼
        ┌──────────────────┐           ┌──────────────────┐
        │   MongoDB Atlas   │           │   Market Data    │
        │   (User Data)     │           │   (mfapi.in)     │
        └──────────────────┘           └──────────────────┘
```

## Key Design Principles

1. **LLM for Explanation Only**: All financial calculations are done by the deterministic `financial_rules.py` engine. The Gemini LLM is used ONLY for generating natural language explanations.

2. **RAG-Grounded Responses**: All AI responses are grounded in a curated knowledge base of financial best practices. The LLM never answers without retrieved context.

3. **Correctness First**: Financial calculations follow standard formulas (EMI, SIP, compound interest) with full transparency about assumptions.

4. **No Hallucinations**: If the system doesn't have enough data, it clearly states this rather than making up information.

## Setup

### Prerequisites

- Python 3.10+
- MongoDB Atlas account
- Google Gemini API key

### Installation

1. Clone and navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file from template:
```bash
cp .env.example .env
```

5. Configure environment variables in `.env`:
```env
# Required
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_DATABASE=clarifi_db
JWT_SECRET_KEY=your-super-secret-key-here
GEMINI_API_KEY=your-gemini-api-key

# Optional
DEBUG=true
```

6. Create logs directory:
```bash
mkdir logs
```

7. Run the application:
```bash
python main.py
```

Or with uvicorn directly:
```bash
uvicorn main:app --reload --port 8000
```

## API Documentation

Once running, access the interactive API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login and get tokens
- `GET /auth/profile` - Get user profile
- `PUT /auth/profile` - Update profile
- `PUT /auth/profile/password` - Change password
- `POST /auth/refresh` - Refresh access token

### Finance
- `GET/POST /finance/income` - Manage income entries
- `GET/POST /finance/expenses` - Manage expense entries
- `GET/POST /finance/investments` - Manage investments
- `GET/POST /finance/loans` - Manage loans
- `GET/POST /finance/insurance` - Manage insurance policies
- `GET/POST /finance/goals` - Manage financial goals
- `GET /finance/dashboard` - Get aggregated dashboard data

### Chat
- `POST /chat/message` - Send message and get AI response
- `GET /chat/history` - Get chat history
- `DELETE /chat/clear` - Clear chat history

### Analytics
- `GET /analytics/summary` - Financial summary
- `GET /analytics/expenses` - Expense analytics
- `GET /analytics/investments` - Investment analytics
- `GET /analytics/trends` - Monthly trends

### Market Data
- `GET /market/mutual-funds/search` - Search mutual funds
- `GET /market/mutual-funds/{code}` - Get MF NAV
- `GET /market/interest-rates` - Current interest rates
- `GET /market/tax-slabs` - Tax slab information

## Project Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── app/
│   ├── __init__.py
│   ├── core/
│   │   ├── config.py      # Settings management
│   │   ├── security.py    # JWT and password hashing
│   │   ├── database.py    # MongoDB connection
│   │   └── dependencies.py # FastAPI dependencies
│   ├── models/
│   │   ├── user.py        # User Pydantic models
│   │   ├── finance.py     # Finance Pydantic models
│   │   └── chat.py        # Chat and RAG models
│   ├── services/
│   │   ├── auth_service.py       # Authentication logic
│   │   ├── finance_service.py    # Finance CRUD operations
│   │   ├── chat_service.py       # Chat orchestration
│   │   ├── analytics_service.py  # Analytics calculations
│   │   ├── rag_engine.py         # ChromaDB RAG engine
│   │   ├── llm_service.py        # Gemini integration
│   │   ├── financial_rules.py    # Deterministic calculations
│   │   └── market_data.py        # External data fetching
│   └── routes/
│       ├── auth.py        # Auth endpoints
│       ├── finance.py     # Finance endpoints
│       ├── chat.py        # Chat endpoints
│       ├── analytics.py   # Analytics endpoints
│       └── market.py      # Market data endpoints
└── logs/                  # Application logs
```

## Financial Calculations

The `financial_rules.py` engine handles all calculations:

- **Income Analysis**: Savings rate, income stability
- **Expense Analysis**: Category health, budget compliance
- **Investment Calculations**: Compound interest, SIP returns, CAGR
- **Loan Calculations**: EMI, affordability, prepayment benefits
- **Goal Planning**: Feasibility analysis, required monthly savings
- **Insurance**: Coverage needs assessment
- **Net Worth**: Complete asset-liability calculation
- **Financial Health Score**: Holistic financial assessment

## RAG Knowledge Base

The RAG engine is pre-seeded with curated financial knowledge covering:

1. Emergency fund guidelines
2. 50/30/20 budgeting rule
3. Investment diversification
4. Tax saving strategies (80C, 80D, etc.)
5. Health insurance planning
6. Debt management
7. Retirement planning
8. Mutual fund basics

## Security

- Passwords hashed with bcrypt
- JWT tokens with configurable expiry
- CORS configured for frontend origin
- Input validation with Pydantic
- No sensitive data in logs

## Development

### Running Tests
```bash
pytest tests/ -v
```

### Code Formatting
```bash
black app/
isort app/
```

### Type Checking
```bash
mypy app/
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `MONGODB_URI` | MongoDB Atlas connection string | Yes |
| `MONGODB_DATABASE` | Database name | Yes |
| `JWT_SECRET_KEY` | Secret for JWT signing | Yes |
| `GEMINI_API_KEY` | Google Gemini API key | Yes |
| `JWT_ALGORITHM` | JWT algorithm (default: HS256) | No |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry (default: 30) | No |
| `CHROMA_PERSIST_DIR` | ChromaDB storage path | No |
| `DEBUG` | Enable debug mode | No |
| `HOST` | Server host (default: 0.0.0.0) | No |
| `PORT` | Server port (default: 8000) | No |

## License

MIT License
