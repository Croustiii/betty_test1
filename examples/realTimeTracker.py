"""
Exemple : se synchronise avec l'horloge systeme
"""
from datetime import datetime
from polymarket.scheduler import CycleScheduler
from polymarket.config import IntervalSec

def debut(dt: datetime):
    print(f"=== DEBUT {dt} ===")

def fin(dt: datetime):
    print(f"=== FIN   {dt} ===")

def main() -> None:
    CycleScheduler(IntervalSec.DEBUG2,tick_seconds = 5, on_cycle_start=debut, on_cycle_end=fin).run()


if __name__ == "__main__":
    main()
