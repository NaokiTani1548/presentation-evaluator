import os

from fastapi import HTTPException  # FastAPI standard exception
from sqlalchemy import inspect  # check if table exists
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
)  # create async engine
from sqlalchemy.orm import sessionmaker, declarative_base  # create session

# define base class
Base = declarative_base()


def configure_database():

    # test用データベースに接続
    base_dir = os.path.dirname(os.path.abspath(__file__))
    database_url = "sqlite+aiosqlite:///" + os.path.join(base_dir, "test_db.sqlite3")

    return database_url


# set DB URL
DATABASE_URL = configure_database()

# create async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# create async session
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


# function to handle DB session asynchronously
async def get_dbsession():
    async with async_session() as session:
        yield session


# initialize DB
# (this function is used to initialize DB when server starts)
async def initialize_database(db: AsyncSession) -> None:
    try:
        # check if table exists
        async with engine.begin() as conn:

            def get_table_names(sync_conn):
                inspector = inspect(sync_conn)
                return inspector.get_table_names()

            table_names = await conn.run_sync(get_table_names)

        # if table does not exist, create table
        if not table_names:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
                print("Database tables created successfully")

    except Exception as e:
        # Log the actual error for debugging
        print(f"Database initialization error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to initialize database")
