from dataclasses import dataclass

# Teal-ink neutrals; one magenta hero.
@dataclass
class Cruise:
    destination: str = "Miami"
    speed: float = 88.0

    def depart(self, passengers: int = 2) -> str:
        if passengers > 0:
            return f"Next stop: {self.destination}"
        raise ValueError("No passengers aboard")
