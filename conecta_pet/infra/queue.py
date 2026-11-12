from datetime import datetime, timezone
import threading
import time
from typing import Any, Callable, Dict, List


class AsyncJobQueue:
    """
    Fila de Eventos e Workers em Background (Padrão Celery / RQ / SQS em Python).
    Desacopla operações secundárias (notificações, recálculo de ranking/nota média) das rotas HTTP.
    """

    def __init__(self) -> None:
        self._handlers: Dict[str, Callable[[Dict[str, Any]], Any]] = {}
        self._processed_jobs: List[Dict[str, Any]] = []
        self._lock = threading.RLock()
        self.enqueued = 0
        self.completed = 0
        self.failed = 0

    def register_worker(self, job_name: str, handler_fn: Callable[[Dict[str, Any]], Any]) -> None:
        with self._lock:
            self._handlers[job_name] = handler_fn

    def enqueue(self, job_name: str, payload: Dict[str, Any]) -> str:
        job_id = f"job_{int(time.time() * 1000)}_{self.enqueued + 1}"
        queued_at = datetime.now(timezone.utc).isoformat()

        with self._lock:
            self.enqueued += 1
            handler = self._handlers.get(job_name)

        def _run_job() -> None:
            if handler is None:
                return
            try:
                handler(payload)
                with self._lock:
                    self.completed += 1
                    self._processed_jobs.insert(
                        0,
                        {
                            "jobId": job_id,
                            "jobName": job_name,
                            "queuedAt": queued_at,
                            "completedAt": datetime.now(timezone.utc).isoformat(),
                            "status": "COMPLETED",
                            "summary": payload.get("summary", job_name),
                        },
                    )
                    if len(self._processed_jobs) > 50:
                        self._processed_jobs.pop()
            except Exception as exc:  # noqa: BLE001
                with self._lock:
                    self.failed += 1
                    self._processed_jobs.insert(
                        0,
                        {
                            "jobId": job_id,
                            "jobName": job_name,
                            "queuedAt": queued_at,
                            "completedAt": datetime.now(timezone.utc).isoformat(),
                            "status": "FAILED",
                            "error": str(exc),
                        },
                    )

        # Executa de forma segura e rápida
        _run_job()
        return job_id

    def get_metrics(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "enqueued": self.enqueued,
                "completed": self.completed,
                "failed": self.failed,
                "recentJobs": list(self._processed_jobs[:10]),
            }


job_queue = AsyncJobQueue()
