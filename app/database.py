import psycopg
from psycopg.rows import dict_row
from sqlalchemy import create_engine, text, Boolean, Column, ForeignKey, Integer, String, TIMESTAMP
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from .settings import settings
from sqlalchemy.orm import relationship

# Psycopg DB Connection and cursor

def get_connection():
    return psycopg.connect(f"user={settings.DB_USER} password={settings.DB_PASSWORD} host={settings.DB_HOSTNAME} port={settings.DB_PORT} dbname={settings.DB_NAME}", row_factory=dict_row)

def get_cursor(connection):
    return connection.cursor()

# SQLAlchemy

SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOSTNAME}:{settings.DB_PORT}/{settings.DB_NAME}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# SQLAlchemy table models

class PostsTable(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    published = Column(Boolean, server_default="TRUE", nullable=False)
    creation_date = Column(TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False)
    last_update = Column(TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False)
    user_id = Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    user_details = relationship("UsersTable")

class UsersTable(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    creation_date = Column(TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False)

class VotesTable(Base):
    __tablename__ = "votes"
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True, nullable=False)

    user = relationship("UsersTable", foreign_keys=[user_id])
    post = relationship("PostsTable", foreign_keys=[post_id])


#Function found in <https://prahladyeri.github.io/blog/2015/07/sqlalchemy-hack-convert-dict.html> to convert
#table objects (returned from queries) to python dicts
# def to_dict(model_instance, query_instance=None):
# 	if hasattr(model_instance, '__table__'):
# 		return {c.name: str(getattr(model_instance, c.name)) for c in model_instance.__table__.columns}
# 	else:
# 		cols = query_instance.column_descriptions
# 		return { cols[i]['name'] : model_instance[i]  for i in range(len(cols)) }
     
# def from_dict(dict, model_instance):
# 	for c in model_instance.__table__.columns:
# 		setattr(model_instance, c.name, dict[c.name])