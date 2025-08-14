from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.config import config


class Connections:
    """Class to manage all third parties connections."""

    engine: AsyncEngine

    def __init__(self) -> None:  # noqa: D107
        self.engine = create_async_engine(url=config.retrieve_db_url, echo=config.LOGS_DB, future=True)
        self.async_session = async_sessionmaker(
            class_=AsyncSession,
            bind=self.engine,
            expire_on_commit=False,
            autoflush=False,
        )

    async def get_db(self) -> AsyncGenerator[AsyncSession]:
        """Get DB connection to use it to store data into the DB.

        Yields:
            AsyncSession: An asynchronous database session.
        """
        db_conn = self.async_session()

        try:
            yield db_conn
        except Exception:  # pylint: disable=W0718
            await db_conn.rollback()
            raise  # NOTE: important to re raise an error, in fastapi otherwise the customer error middleware wont work
        finally:
            await db_conn.close()


connections = Connections()
