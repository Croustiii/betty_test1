import threading
import time
from datetime import datetime
from typing import Callable, Optional


class CycleScheduler:
    """Boucle infinie calée sur l'heure système, cadencée par un intervalle en secondes.

    Chaque cycle démarre sur un multiple fixe de l'horloge système (ex: 10:00, 10:05…).
    Le callback on_cycle_start est exécuté dans un thread dédié pour ne pas bloquer la boucle
    principale, ce qui permet des appels vers des APIs externes sans perturber le cadencement.
    Si le thread du cycle précédent est toujours actif au démarrage du suivant, le cycle est
    ignoré avec un avertissement (protection contre le chevauchement).
    Les exceptions levées dans les callbacks sont catchées et loguées sans arrêter le scheduler.

    Args:
        interval_seconds: durée d'un cycle en secondes (ex: IntervalSec.DEBUG2)
        tick_seconds: fréquence d'affichage heure + pourcentage à l'intérieur d'un cycle
        on_cycle_start: appelé en début de cycle dans un thread séparé
        on_cycle_end: appelé en fin de cycle sur le thread principal (signal indépendant)
    """

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
        self._current_thread: Optional[threading.Thread] = None

    def _next_boundary(self) -> float:
        """Retourne le timestamp Unix du prochain multiple de l'intervalle."""
        now = time.time()
        return (now // self.interval_seconds + 1) * self.interval_seconds

    def _safe_call(self, fn: Callable, dt: datetime) -> None:
        """Exécute fn(dt) en isolant les exceptions pour ne pas interrompre le scheduler."""
        try:
            fn(dt)
        except Exception as e:
            print(f"[ERROR] Callback échoué : {e}")

    def run(self) -> None:
        """Démarre la boucle de cycles. Bloque indéfiniment — Ctrl+C pour arrêter proprement."""
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

                if self._current_thread and self._current_thread.is_alive():
                    print(f"[WARNING] [{datetime.now().strftime('%H:%M:%S')}] Cycle précédent toujours en cours, ignoré")
                else:
                    self._current_thread = threading.Thread(
                        target=self._safe_call,
                        args=(self.on_cycle_start, datetime.fromtimestamp(cycle_start)),
                        daemon=True,
                    )
                    self._current_thread.start()

                while True:
                    time.sleep(self.tick_seconds)
                    now = time.time()
                    elapsed = now - cycle_start
                    pct = min(elapsed / self.interval_seconds * 100, 100.0)
                    print(f"  {datetime.now().strftime('%H:%M:%S.%f')[:-3]}  |  {pct:5.1f}%")
                    if now >= cycle_end:
                        break

                self._safe_call(self.on_cycle_end, datetime.now())

        except KeyboardInterrupt:
            print("Scheduler arrêté.")
