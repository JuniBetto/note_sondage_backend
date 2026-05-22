# decorators/cache_decorator.py
from functools import wraps
import json
from typing import Optional, Any
import hashlib

class CacheDecorator:
    def __init__(self, cache_service, ttl: int = 3600):
        self.cache_service = cache_service
        self.ttl = ttl
    
    def __call__(self, func):
        @wraps(func)
        async def wrapper(instance, *args, **kwargs):
            # Genera una chiave unica per la cache
            cache_key = self._generate_cache_key(func.__name__, args, kwargs)
            
            # Prova a recuperare dalla cache
            cached = await self.cache_service.get(cache_key)
            if cached is not None:
                return self._deserialize(cached)
            
            # Se non in cache, esegui la funzione originale
            result = await func(instance, *args, **kwargs)
            
            # Salva in cache se il risultato non è None
            if result is not None:
                await self.cache_service.set(
                    cache_key, 
                    self._serialize(result), 
                    ttl=self.ttl
                )
            
            return result
        
        return wrapper
    
    def _generate_cache_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Genera una chiave unica per la cache"""
        key_data = f"{func_name}:{args}:{sorted(kwargs.items())}"
        return f"tipi:{hashlib.md5(key_data.encode()).hexdigest()}"
    
    def _serialize(self, entity) -> str:
        """Serializza l'entità per la cache"""
        return json.dumps(entity.to_dict() if hasattr(entity, 'to_dict') else vars(entity))
    
    def _deserialize(self, data: str, default: Any = None):
        """Deserializza i dati con supporto per tipi complessi"""
        try:
            # Se i dati sono già None o vuoti
            if not data:
                return default
                
            loaded = json.loads(data)
            
            # Se non è specificato un tipo di default, restituisci i dati grezzi
            if default is None:
                return loaded
                
            # Se default è una classe/costruttore
            if isinstance(default, type):
                return self._create_instance(default, loaded)
            # Se default è un'istanza (usiamo la sua classe)
            else:
                return self._create_instance(default.__class__, loaded)
                
        except Exception as e:
            logger.error(f"Errore deserializzazione: {e}")
            return default  # Fallback al valore di default
        

    def _create_instance(self, cls, data):
        """Crea un'istanza da un dizionario"""
        # Controlla se la classe ha un metodo di deserializzazione
        if hasattr(cls, 'from_dict'):
            return cls.from_dict(data)
        # Altrimenti usa il costruttore standard
        elif isinstance(data, dict):
            return cls(**data)
        # Per dati semplici (int, str, list, etc.)
        else:
            return cls(data)