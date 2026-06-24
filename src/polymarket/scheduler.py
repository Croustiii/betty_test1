import time
from datetime import datetime
from typing import Callable, Optional


class CycleScheduler:
    """Boucle infinie calée sur l'heure système, cadencée par un intervalle en secondes."""

    def __init__(
        self,
        interval_seconds: int,
        tick_seconds: int = 1,
        on_cycle_start: Optional[Callable[[datetime], None]] = None,
        on_cycle_end: Optional[Callable[[datetime], None]] = None,
    ):
        if interval_seconds <= 0:
            raise ValueError("interval_seconds doit être strictement positif")
        if not (0 < tick_seconds <= interval_seconds):
            raise ValueError("tick_seconds doit être entre 1 et interval_seconds")
        self.interval_seconds = interval_seconds
        self.tick_seconds = tick_seconds
        self.on_cycle_start = on_cycle_start or (lambda dt: print(f"[{dt.strftime('%H:%M:%S')}] Début du cycle ({interval_seconds}s)"))
        self.on_cycle_end = on_cycle_end or (lambda dt: print(f"[{dt.strftime('%H:%M:%S')}] Fin du cycle"))

    def _next_boundary(self) -> float:
        """Retourne le timestamp Unix du prochain multiple de l'intervalle."""
        now = time.time()
        return (now // self.interval_seconds + 1) * self.interval_seconds

    def run(self) -> None:
        """Démarre la boucle. Bloque indéfiniment (KeyboardInterrupt pour arrêter)."""
        print(f"Scheduler démarré — intervalle : {self.interval_seconds}s, tick : {self.tick_seconds}s")
        try:
            next_start = self._next_boundary()
            while True:
                wait = next_start - time.time()
                if wait > 0:
                    time.sleep(wait)

                cycle_start = next_start
                next_start = cycle_start + self.interval_seconds
                cycle_end = next_start
                self.on_cycle_start(datetime.fromtimestamp(cycle_start))

                while True:
                    time.sleep(self.tick_seconds)
                    now = time.time()
                    elapsed = now - cycle_start
                    pct = min(elapsed / self.interval_seconds * 100, 100.0)
                    print(f"  {datetime.now().strftime('%H:%M:%S.%f')[:-3]}  |  {pct:5.1f}%")
                    if now >= cycle_end:
                        break

                self.on_cycle_end(datetime.now())

        except KeyboardInterrupt:
            print("Scheduler arrêté.")
