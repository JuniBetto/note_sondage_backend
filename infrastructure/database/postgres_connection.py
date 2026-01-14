# app_backend/infrastructure/database/postgres_connection.py
import psycopg2
import psycopg2.extras
from psycopg2.pool import SimpleConnectionPool
from contextlib import contextmanager
import os
from typing import Generator, Dict, Any, List, Optional
from datetime import datetime
import json
from decimal import Decimal
from dotenv import load_dotenv
load_dotenv()


# DEBUG: Stampa le variabili per verificare
print("=== VARIABILI D'AMBIENTE ===")
print(f"DB_HOST: {os.getenv('DB_HOST', 'NON SET')}")
print(f"DB_PORT: {os.getenv('DB_PORT', 'NON SET')}")
print(f"DB_NAME: {os.getenv('DB_NAME', 'NON SET')}")
print(f"DB_USER: {os.getenv('DB_USER', 'NON SET')}")
print(f"DB_PASSWORD: {os.getenv('DB_PASSWORD', 'NON SET')}")
print("============================")

class PostgresConnection:
    """Gestione diretta delle connessioni PostgreSQL con cursori."""
    
    def __init__(self):
        self._pool = None
        
    def _get_connection_params(self) -> Dict[str, Any]:
        """Recupera parametri di connessione da environment variables."""
        return {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'mydb'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', ''),
            'application_name': 'note_sondage_app'
        }
    
    def get_pool(self) -> SimpleConnectionPool:
        """Crea o restituisce il pool di connessioni."""
        if self._pool is None:
            params = self._get_connection_params()
            self._pool = SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                **params
            )
        return self._pool
    
    @contextmanager
    def get_connection(self) -> Generator:
        """Context manager per ottenere una connessione dal pool."""
        pool = self.get_pool()
        conn = pool.getconn()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            pool.putconn(conn)
    
    @contextmanager
    def get_cursor(self, cursor_factory=None) -> Generator:
        """Context manager per ottenere un cursore."""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=cursor_factory)
            try:
                yield cursor
            finally:
                cursor.close()
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """Esegue una query SELECT e restituisce i risultati."""
        with self.get_cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchall()
    
    def execute_all_modify(self, query: str, params: tuple = None) -> int:
        """Esegue una query INSERT/UPDATE/DELETE e restituisce il numero di righe."""
        with self.get_cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.rowcount

    def execute_insert(self, query: str, params: tuple = None, return_columns: list = None) -> Dict[str, Any]:
        """
        Esegue una query INSERT e restituisce i dati inseriti.

        Args:
            query: Query SQL INSERT
                params: Parametri per la query
                return_columns: Colonne da restituire (usare RETURNING)
                
            Returns:
                Dict con i nuovi valori
            """
        with self.get_cursor() as cursor:
            # Aggiungi RETURNING se non presente e specificato
            if return_columns and "RETURNING" not in query.upper():
                query = f"{query.rstrip(';')} RETURNING {', '.join(return_columns)}"
            
            cursor.execute(query, params or ())
            
            result = {
                "operation": "INSERT",
                "timestamp": datetime.now().isoformat(),
                "new": {}
            }
            
            # Se c'è RETURNING, ottieni i dati
            if "RETURNING" in query.upper():
                row = cursor.fetchone()
                if row:
                    columns = [desc[0] for desc in cursor.description]
                    result["new"] = dict(zip(columns, row))
            
            result["affected_rows"] = cursor.rowcount
            return result
    
    def execute_update(self, query: str, params: tuple = None,
                      get_old_values_query: str = None, 
                      get_old_params: tuple = None) -> Dict[str, Any]:
        """
        Esegue una query UPDATE e restituisce vecchi e nuovi valori.
        
        Args:
            query: Query SQL UPDATE
            params: Parametri per l'UPDATE
            get_old_values_query: Query per ottenere i vecchi valori
            get_old_params: Parametri per la query dei vecchi valori
            
        Returns:
            Dict con old e new values
        """
        with self.get_cursor() as cursor:
            # PRIMA: Ottieni i vecchi valori se possibile
            old_values = {}
            if get_old_values_query:
                cursor.execute(get_old_values_query, get_old_params or ())
                row = cursor.fetchone()
                if row:
                    columns = [desc[0] for desc in cursor.description]
                    old_values = dict(zip(columns, row))
            
            # ESEGUI l'UPDATE
            cursor.execute(query, params or ())
            
            # DOPO: Ottieni i nuovi valori se c'è RETURNING
            result = {
                "operation": "UPDATE",
                "timestamp": datetime.now().isoformat(),
                "old": old_values,
                "new": {}
            }
            
            # Cerca RETURNING per ottenere nuovi valori
            if "RETURNING" in query.upper():
                row = cursor.fetchone()
                if row:
                    columns = [desc[0] for desc in cursor.description]
                    result["new"] = dict(zip(columns, row))
            
            result["affected_rows"] = cursor.rowcount
            return result
    
    def execute_delete(self, query: str, params: tuple = None,
                      get_old_values_query: str = None,
                      get_old_params: tuple = None) -> Dict[str, Any]:
        """
        Esegue una query DELETE e restituisce i vecchi valori.
        
        Args:
            query: Query SQL DELETE
            params: Parametri per il DELETE
            get_old_values_query: Query per ottenere i valori eliminati
            get_old_params: Parametri per la query dei valori eliminati
            
        Returns:
            Dict con old values
        """
        with self.get_cursor() as cursor:
            # PRIMA: Ottieni i vecchi valori se possibile
            old_values = {}
            if get_old_values_query:
                cursor.execute(get_old_values_query, get_old_params or ())
                row = cursor.fetchone()
                if row:
                    columns = [desc[0] for desc in cursor.description]
                    old_values = dict(zip(columns, row))
            
            # ESEGUI il DELETE
            cursor.execute(query, params or ())
            
            result = {
                "operation": "DELETE",
                "timestamp": datetime.now().isoformat(),
                "old": old_values,
                "affected_rows": cursor.rowcount
            }
            
            return result
    
    def execute_crud(self, query: str, params: tuple = None,
                    operation: str = None) -> Dict[str, Any]:
        """
        Metodo universale che riconosce automaticamente il tipo di operazione.
        
        Args:
            query: Query SQL
            params: Parametri
            operation: Forza il tipo di operazione (INSERT/UPDATE/DELETE)
            
        Returns:
            Dict con i risultati appropriati
        """
        # Determina il tipo di operazione
        if operation:
            op_type = operation.upper()
        else:
            op_type = query.strip().upper().split()[0]
        
        if op_type == "INSERT":
            return self.execute_insert(query, params)
        elif op_type == "UPDATE":
            return self.execute_update(query, params)
        elif op_type == "DELETE":
            return self.execute_delete(query, params)
        else:
            raise ValueError(f"Operazione non supportata: {op_type}")

    def execute_scalar(self, query: str, params: tuple = None) -> Any:
        """Esegue una query e restituisce un singolo valore."""
        with self.get_cursor() as cursor:
            cursor.execute(query, params or ())
            result = cursor.fetchone()
            return result[0] if result else None
    
    def close_all(self):
        """Chiude tutte le connessioni nel pool."""
        if self._pool:
            self._pool.closeall()