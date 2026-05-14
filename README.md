----------flow----------

User clicks "Create Note"
        ↓
Frontend sends API request
        ↓
FastAPI receives request
        ↓
Backend validates data
        ↓
Stores note in PostgreSQL
        ↓
Returns response


to run the app: uvicorn app.main:app --reload                       

for requoirements.txtx: pip freeze > requirements.txt

for installing those packages: pip install -r requirements.txt

pip install:

pip install fastapi uvicorn

pip install sqlalchemy psycopg2-binary python-dotenv

pip install alambic

alembic init alembic

pip install python-jose passlib bcrypt python-multipart[email-validator]

env flow
.env file
   ↓
load_dotenv()
   ↓
Environment Variables Loaded
   ↓
os.getenv()
   ↓
Python can access them


alambic: for migration perpose

alembic revision --autogenerate -m "add app tables" 

alembic upgrade head


| Package          | Purpose                       |
| ---------------- | ----------------------------- |
| python-jose      | JWT handling                  |
| passlib          | Password hashing              |
| bcrypt           | Secure hashing                |
| python-multipart | Form handling                 |
| email-validator  | Email validation for Pydantic |


--------register flow--------

Request arrives
      ↓
Pydantic validates data
      ↓
Password hashed
      ↓
User object created
      ↓
Saved to PostgreSQL
      ↓
Success response returned