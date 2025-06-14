# JITORM: Just-In-Time Optimized Python ORM

JITORM is a Python-based Object-Relational Mapping (ORM) framework enhanced with Just-In-Time (JIT) compilation to optimize data mapping performance. Developed for data-intensive environments, it significantly reduces execution time, memory usage, and CPU load compared to traditional ORM frameworks.

## 🚀 Key Features

- Declarative model definition
- Backend support for PostgreSQL, MySQL, and SQLite
- JIT compilation using LLVM (via llvmlite)
- Optimized object mapping layer
- Compatible with Flask and FastAPI
- Efficient for large dataset processing and batch operations

---

## 📦 Installation

Install directly from GitHub using:

```bash
pip install git+git://github.com/akarkode/jitorm.git
```

Or via HTTPS if preferred:

```bash
pip install git+https://github.com/akarkode/jitorm.git
```

---

## 🧩 Example Usage

### `model.py`

```python
from jitorm.orm.models import Model
from jitorm.orm.fields import IntegerField, StringField

class Users(Model):
    id = IntegerField(primary_key=True)
    username = StringField()
    password = StringField()
    name = StringField()
    address = StringField()
    email = StringField()
    job = StringField()
    birthdate = StringField()
    phone_number = StringField()
```

### `crud.py`

```python
from jitorm.orm.session import Session

class CRUD:

    @staticmethod
    def create(db: Session, model, data):
        record = model(**data)
        db.add(record)
        db.commit()
        return record

    @staticmethod
    def get_by_id(db: Session, model, id):
        record = db.query(model).filter(id=id).first()
        if not record:
            print(f"Data with id {id} not found.")
            return
        return record

    @staticmethod
    def get_list(db: Session, model):
        return db.query(model).all()

    @staticmethod
    def update(db: Session, model, filters, **kwargs):
        db.update(model, filters, **kwargs)
        db.commit()
        return

    @staticmethod
    def delete(db: Session, model, filters):
        db.delete(model, filters)
        db.commit()
        return

    @staticmethod
    def bulk_create(db: Session, model, data):
        db.bulk_create(model=model, items=data)
        return
```

---

## 🔧 Integration Example (FastAPI)

```python
from fastapi import FastAPI, Depends
from jitorm.orm.postgresql import DatabaseConnection
from jitorm.orm.session import Session
from models import Users
from crud import CRUD

app = FastAPI()
db_conn = DatabaseConnection(
    host="localhost",
    port=5432,
    user="postgres",
    password="yourpassword",
    database="yourdb"
)

def get_db():
    with Session(db_conn) as db:
        yield db

@app.post("/users")
def create_user(data: dict, db=Depends(get_db)):
    return CRUD.create(db, Users, data)

@app.get("/users/{user_id}")
def get_user(user_id: int, db=Depends(get_db)):
    return CRUD.get_by_id(db, Users, user_id)
```

---

## 📚 Academic Background

This project is based on the master's thesis:

> "Enhancing Python Object-Relational Mapping Performance using Just-In-Time Compiler"  
> by Aldi Setiawan — Telkom University, 2025

---

## 🛠 Dependencies

- `mysqlclient`
- `psycopg2-binary`
- `llvmlite`
- `numpy`

---

## 📄 License

MIT License © 2025 AKARKODE