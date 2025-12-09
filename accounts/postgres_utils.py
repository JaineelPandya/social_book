"""
PostgreSQL utilities using SQLAlchemy for direct database access.
This allows querying PostgreSQL databases directly without Django ORM.
"""

from sqlalchemy import create_engine, text
import logging

logger = logging.getLogger(__name__)


class PostgreSQLConnection:
    """Helper class to manage PostgreSQL connections via SQLAlchemy."""
    
    _engine = None
    
    @classmethod
    def get_engine(cls, db_url=None):
        """Get or create SQLAlchemy engine for PostgreSQL.
        
        Args:
            db_url: PostgreSQL connection string. Example:
                    postgresql://username:password@localhost:5432/database_name
        
        Returns:
            SQLAlchemy engine instance
        """
        if cls._engine is None and db_url:
            try:
                cls._engine = create_engine(db_url, echo=False)
                logger.info(f"PostgreSQL connection established: {db_url}")
            except Exception as e:
                logger.error(f"Failed to connect to PostgreSQL: {e}")
                return None
        
        return cls._engine
    
    @classmethod
    def execute_query(cls, query_str, db_url=None, params=None):
        """Execute a SQL query against PostgreSQL.
        
        Args:
            query_str: SQL query string
            db_url: PostgreSQL connection string (optional if engine exists)
            params: Query parameters dict for parameterized queries
        
        Returns:
            List of dictionaries representing result rows, or empty list on error
        """
        try:
            engine = cls.get_engine(db_url) if db_url else cls._engine
            
            if engine is None:
                logger.warning("No PostgreSQL connection available")
                return []
            
            with engine.connect() as conn:
                result = conn.execute(text(query_str), params or {})
                # Convert Row objects to dictionaries
                return [dict(row._mapping) for row in result.fetchall()]
        
        except Exception as e:
            logger.error(f"Query execution error: {e}")
            return []
    
    @classmethod
    def disconnect(cls):
        """Close the engine connection."""
        if cls._engine:
            cls._engine.dispose()
            cls._engine = None
            logger.info("PostgreSQL connection closed")


def get_users_summary(db_url):
    """Fetch summary of users from PostgreSQL.
    
    This is a sample query showing how to fetch data directly from PostgreSQL.
    """
    query = """
    SELECT 
        COUNT(*) as total_users,
        COUNT(CASE WHEN public_visibility = true THEN 1 END) as public_users,
        COUNT(CASE WHEN is_active = true THEN 1 END) as active_users
    FROM accounts_customuser;
    """
    
    results = PostgreSQLConnection.execute_query(query, db_url)
    return results[0] if results else {}


def get_files_stats(db_url):
    """Fetch file upload statistics from PostgreSQL."""
    query = """
    SELECT 
        COUNT(*) as total_files,
        SUM(file_size) as total_size,
        AVG(file_size) as avg_size,
        MAX(file_size) as max_size,
        COUNT(DISTINCT user_id) as users_with_files
    FROM accounts_uploadedfile
    WHERE is_active = true;
    """
    
    results = PostgreSQLConnection.execute_query(query, db_url)
    return results[0] if results else {}


def get_recent_uploads(db_url, limit=10):
    """Fetch recent file uploads from PostgreSQL."""
    query = """
    SELECT 
        f.id,
        f.title,
        f.file,
        f.file_size,
        f.uploaded_at,
        f.visibility,
        u.email as user_email
    FROM accounts_uploadedfile f
    JOIN accounts_customuser u ON f.user_id = u.id
    WHERE f.is_active = true
    ORDER BY f.uploaded_at DESC
    LIMIT :limit;
    """
    
    results = PostgreSQLConnection.execute_query(query, db_url, {'limit': limit})
    return results
