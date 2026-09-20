
import os
# from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel import SQLModel, create_engine


class DatabaseConnection:
    """
    Manages the PostgreSQL engine and connection pool.

    One instance per FastAPI process.
    """

    def __init__(self) -> None:
        try:
            self.database_url = os.getenv("DATABASE_URL")

            if not self.database_url:
                raise RuntimeError(
                    "DATABASE_URL environment variable is missing"
                )

            if not self.database_url.startswith(
                "postgresql+psycopg://"
            ):
                raise RuntimeError(
                    "DATABASE_URL must use "
                    "postgresql+psycopg://"
                )

            # Create the SQLAlchemy engine
            self.engine = create_engine(
                self.database_url,
                # echo=True,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                pool_recycle=1800,
            )

            print("Database initialized !!!")

        except Exception as e:
            print(f"Error initializing database: {e}")
            raise

    def create_tables(self) -> None:
        """
        Creates tables if they do not exist.

        Use migrations for production schema changes.
        """
        try:
            SQLModel.metadata.create_all(self.engine) # Create all tables defined in the SQLModel classes
            print("Tables created !!!")
        except Exception as e:
            print(f"Error creating tables: {e}")
            raise

    def get_engine(self):
        """
        Returns the shared SQLModel engine.
        """
        try:
            return self.engine
        except Exception as e:
            print(f"Error getting engine: {e}")
            raise

    def dispose(self) -> None:
        """
        Releases the connection pool.
        """
        try:
            self.engine.dispose()
            print("Connection pool disposed !!!")
        except Exception as e:
            print(f"Error disposing engine: {e}")
            raise


# class DatabaseLifecycle:
#     """
#     Handles application startup and shutdown.
#     """

#     def __init__(
#         self,
#         database: DatabaseConnection,
#     ) -> None:
#         self.database = database
# tables = DatabaseConnection()

# tables.create_tables()