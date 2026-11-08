from dataclasses import dataclass

@dataclass
class Cruise:
    destination: str = "Ocean Drive"
    speed: float = 55.0

    def depart(self, passengers: int = 1) -> str:
        return f"Leaving for {self.destination}"
