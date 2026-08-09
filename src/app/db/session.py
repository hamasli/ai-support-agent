# This create the database connection between the database and the our python application.
from sqlalchemy import create_engine;
# This creates database sessions that we will use to actually run queries.
from sqlalchemy.orm import sessionmaker;
from src.app.core.config import settings;
from sqlalchemy import text;




#this creatres the SQLALchemy engine.
# the main connection manager between your pythgon app and postgresql.
engine=create_engine(
    settings.database_url,
    echo=False,
)
SessionLocal=sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


# for just testing the connection.
# with engine.connect() as connection:
#     result = connection.execute(
#         text("SELECT current_database();")
#     )

#     print(result.scalar())



