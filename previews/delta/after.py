from dataclasses import dataclass

@dataclass
class Cruise:
    destination: str = "Miami Beach"
    speed: float = 88.0

    def depart(self, passengers: int = 2) -> str:
        if passengers < 1:
            raise ValueError("No passengers aboard")
        return f"Next stop: {self.destination}"
