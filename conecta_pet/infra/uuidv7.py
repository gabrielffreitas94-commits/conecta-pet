import os
import time
import uuid


def uuidv7() -> str:
    """
    Gera um UUIDv7 (RFC 9562) ordenado temporalmente (time-sortable).
    Evita fragmentação de índices B-Tree em bancos PostgreSQL/SQLite sob alta carga de escrita.
    """
    timestamp_ms = int(time.time() * 1000) & 0xFFFFFFFFFFFF
    rand_bytes = bytearray(os.urandom(10))

    # Versão 7 (0111 nos 4 bits mais significativos do byte 6)
    rand_bytes[0] = (rand_bytes[0] & 0x0F) | 0x70
    # Variante RFC 4122 (10xx nos 2 bits mais significativos do byte 8)
    rand_bytes[2] = (rand_bytes[2] & 0x3F) | 0x80

    ts_bytes = timestamp_ms.to_bytes(6, byteorder="big")
    raw = ts_bytes + bytes(rand_bytes)
    return str(uuid.UUID(bytes=raw))
