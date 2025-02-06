import os
import psycopg2
from typing import Dict, Optional
from psycopg2.extras import DictCursor

class SupabaseClient:
    """Manages PostgreSQL connections and operations for Supabase"""
    
    def __init__(self):
        self.config = {
            'host': os.getenv("SUPABASE_HOST"),
            'port': os.getenv("SUPABASE_PORT", 5432),
            'database': os.getenv("SUPABASE_DB"),
            'user': os.getenv("SUPABASE_USER"),
            'password': os.getenv("SUPABASE_PASSWORD"),
            'cursor_factory': DictCursor
        }
        self.connection = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def connect(self):
        """Establish database connection"""
        if not self.connection or self.connection.closed:
            self.connection = psycopg2.connect(**self.config)

    def disconnect(self):
        """Close database connection"""
        if self.connection and not self.connection.closed:
            self.connection.close()

    def check_existing_entry(self, full_name: str) -> bool:
        """Check if entry exists in the database"""
        with self.connection.cursor() as cursor:
            check_query = '''
                SELECT EXISTS (
                    SELECT 1 FROM public."KoboOptionUpdateTest"
                    WHERE LOWER(CONCAT(
                        nombre, ' ', 
                        "apellido paterno", ' ', 
                        COALESCE("apellido materno", '')
                    )) = LOWER(%s)
                )
            '''
            cursor.execute(check_query, (full_name,))
            return cursor.fetchone()[0]

    def insert_registration(self, data: Dict) -> bool:
        """Insert new registration into database"""
        with self.connection.cursor() as cursor:
            # Get table columns
            cursor.execute('''
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = 'KoboOptionUpdateTest'
            ''')
            table_columns = [col[0] for col in cursor.fetchall()]

            # Prepare data
            normalized_data = {
                self._normalize_key(k): v 
                for k, v in data.items()
                if self._normalize_key(k) in table_columns
            }

            # Build and execute insert query
            columns = [f'"{col}"' for col in normalized_data.keys()]
            placeholders = ', '.join(['%s'] * len(normalized_data))
            query = f'''
                INSERT INTO public."KoboOptionUpdateTest" ({', '.join(columns)})
                VALUES ({placeholders})
            '''
            cursor.execute(query, list(normalized_data.values()))
            self.connection.commit()
            return True

    @staticmethod
    def _normalize_key(key: str) -> str:
        """Normalize keys to match database column names"""
        return key.replace('_', ' ').lower()