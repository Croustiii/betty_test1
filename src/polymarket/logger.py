import threading
from datetime import datetime
from pathlib import Path


class Logger:
    """Ecrit les logs simultanément sur la console et dans un fichier horodaté.

    Thread-safe — plusieurs threads peuvent appeler log() en parallèle sans interleaving.
    Un fichier unique est créé par instanciation, nommé avec la date et l'heure de lancement.
    """

    def __init__(self, log_dir: str = "logs") -> None:
        self._lock = threading.Lock()
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_path = Path(log_dir) / f"{ts}.log"
        self._file = open(log_path, "w", encoding="utf-8", buffering=1)
        self._info(f"Session démarrée — {log_path}")

    def log(self, thread_id: str, label: str, msg: str) -> None:
        """Log formaté avec identifiant de thread et label."""
        self._write(f"  [T:{thread_id}][{label}] {msg}")

    def info(self, msg: str) -> None:
        """Log système sans thread_id (démarrage, arrêt, warnings scheduler)."""
        self._info(msg)

    def _info(self, msg: str) -> None:
        self._write(f"[INFO] {msg}")

    def _write(self, line: str) -> None:
        with self._lock:
            print(line)
            self._file.write(line + "\n")

    def close(self) -> None:
        self._info("Session terminée.")
        self._file.close()

    def __enter__(self) -> "Logger":
        return self

    def __exit__(self, *args) -> None:
        self.close()
