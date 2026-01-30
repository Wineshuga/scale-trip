# Scale-Trip

**Scale-Trip** is a backend API for managing shared expenses among friends on trips. It allows users to create trips, add participants, log expenses, and track balances. Built with Python, FastAPI, SQLModel, and PostgreSQL, it is async-ready and can be containerized with Docker.

---

## **Features (MVP)**

- Create, list, and retrieve **Users**
- Create, list, and retrieve **Trips**
- Add **Expenses** to trips
- Async database operations with PostgreSQL
- Automatic database table creation on startup
- Interactive API documentation via Swagger (`/docs`)

---

## **Tech Stack**

- **Python 3.12+**
- **FastAPI** – backend framework
- **SQLModel** – ORM + Pydantic for models and validation
- **PostgreSQL** – relational database
- **asyncpg** – async PostgreSQL driver
- **Uvicorn** – ASGI server
- **Docker & Docker Compose** – containerization for local development and deployment

---

## **Installation (Local without Docker)**

1. Clone the repository:

```bash
git clone https://github.com/wineshuga/scale-trip.git
cd scale-trip
```
2. Create a virtual environment and activate it:

```bash
  python3 -m venv .venv
  source .venv/bin/activate
```

3. Install dependencies:

```bash
  pip install -r requirements.txt
```

4. Create a .env file with your database URL:

```bash
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=dbname
DATABASE_URL=postgresql+asyncpg://username:password@db:5432/scale_trip
SECRET_KEY=secret
ALGORITHM=algorithm
ACCESS_TOKEN_EXPIRE_MINUTES=minutes

```

## **Running with Docker**

You can run the app and PostgreSQL together using Docker Compose.

 - Build and start containers:
  
```bash
  docker-compose up --build
```

Access the API at http://127.0.0.1:8000

Interactive API docs: http://127.0.0.1:8000/docs

- To stop containers:

```bash
  docker-compose down
```

Notes:

The docker-compose.yml sets up both the FastAPI app and PostgreSQL database.

Database data is persisted using Docker volumes.

Environment variables are read from .env automatically in the containers.

## **Project Structure**
```bash
scale-trip/
├── app/
|   ├── routers/        # Application routers and endpoints
|   ├── services/       # Application logic
|   ├── auth.py         # User authentication
│   ├── main.py         # FastAPI app and routes
│   ├── models.py       # SQLModel database models
│   ├── database.py     # DB engine and async session setup
|   ├── schemas.py     
│   └── config.py       # Environment configuration
├── docker-compose.yml  # Docker Compose configuration
├── Dockerfile          # Dockerfile for the FastAPI app
├── .env                # Environment variables 
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation
```
## **Usage**

- Users

  - POST /users → create a new user
  - GET /users → list all users
  - GET /users/{user_id} → retrieve a single user

- Trips

  - POST /trips → create a new trip
  - GET /trips → list all trips
  - GET /trips/{trip_id} → retrieve a single trip

- Expenses

  - POST /expenses → create a new expense
  - GET /expenses → list all expenses
  - GET /expenses/{expense_id} → retrieve a single expense

- Payments
  - GET /wallet/{user_id} → get user wallet details
  - POST /wallet/topup-request → mock paystack wallet top up
  - POST /wallet/confirm → Admin/dev endpoint for topup confirmation
  - POST /wallet/pay → execute payment using calculated balance

## **Future Features**

- Dockerized production deployment on AWS ECS/Fargate
- Track user payment status and history
- Integrate wallets and 3rd-party payment (Paystack)

## **License**
