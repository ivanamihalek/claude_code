import os

#  DSN stands for Data Source Name. For PostgreSQL, it is a single string or URL that contains all the required
#  information to locate and connect to your database—including the host, port, database name, username, and password.
# for example
# postgresql://username:password@hostname:port/database_name?sslmode=require

def get_dsn() -> str:
    """Read DATABASE_URL from environment; raise if missing."""
    dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        raise EnvironmentError("DATABASE_URL environment variable is not set.")
    return dsn
