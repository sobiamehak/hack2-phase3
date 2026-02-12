from sqlmodel import create_engine, Session
from sqlalchemy.pool import StaticPool, QueuePool
from dotenv import load_dotenv
import os

# Resolve backend dir first, then load .env from there explicitly
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BACKEND_DIR, ".env"), override=True)
DB_PATH = os.path.join(BACKEND_DIR, "chatbot.db")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")

# For SQLite relative paths, resolve against backend directory
if DATABASE_URL.startswith("sqlite:///./"):
    relative_db = DATABASE_URL.replace("sqlite:///./", "")
    DATABASE_URL = f"sqlite:///{os.path.join(BACKEND_DIR, relative_db)}"

# SQLite needs special pooling config
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
else:
    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=300,
        pool_timeout=30,
        echo=False,
    )


def get_session():
    with Session(engine) as session:
        yield session
