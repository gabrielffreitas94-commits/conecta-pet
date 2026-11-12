import threading
import time
from typing import Any, Dict, Optional


class ScalableGeoCache:
    """
    Camada de Cache em Memória Thread-Safe com suporte a TTL e invalidação por prefixo.
    Projetada com a mesma semântica do Redis Cluster para grande escala.
    """

    def __init__(self) -> None:
        self._store: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()
        self.hits = 0
        self.misses = 0
        self.sets = 0
        self.invalidations = 0

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                self.misses += 1
                return None
            if time.time() > entry["expires_at"]:
                del self._store[key]
                self.misses += 1
                return None
            self.hits += 1
            return entry["value"]

    def set(self, key: str, value: Any, ttl_seconds: float = 30.0) -> None:
        with self._lock:
            self._store[key] = {
                "value": value,
                "expires_at": time.time() + ttl_seconds,
            }
            self.sets += 1

    def invalidate_prefix(self, prefix: str) -> int:
        with self._lock:
            keys_to_remove = [k for k in self._store if k.startswith(prefix)]
            for k in keys_to_remove:
                del self._store[k]
            removed = len(keys_to_remove)
            self.invalidations += removed
            return removed

    def get_metrics(self) -> Dict[str, Any]:
        with self._lock:
            total = self.hits + self.misses
            hit_rate = round((self.hits / total) * 100.0, 1) if total > 0 else 0.0
            return {
                "hits": self.hits,
                "misses": self.misses,
                "sets": self.sets,
                "invalidations": self.invalidations,
                "activeKeys": len(self._store),
                "hitRatePercent": hit_rate,
            }


cache = ScalableGeoCache()
