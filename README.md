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
- **Docker (optional)** – containerization for deployment

---

## **Installation**

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
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/scale_trip
```

---

## **Running the Application**

1. Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

2. Open your browser at http://127.0.0.1:8000

3. Interactive API docs: http://127.0.0.1:8000/docs

## **Project Structure**
```bash
scale-trip/
├── app/
│   ├── main.py         # FastAPI app and routes
│   ├── models.py       # SQLModel database models
│   ├── database.py     # DB engine and async session setup
│   └── config.py       # Environment configuration
├── .env                # Environment variables (not committed)
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
  - Coming soon: create, list, and associate expenses with trips and participants

## **Next Steps / Future Features**

- Add full Expenses CRUD
- Track balances per participant
- Integrate wallets and 3rd-party payment (Paystack)
- Dockerize the application for deployment
- Authentication and user management

## **License**

