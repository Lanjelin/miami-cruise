from dataclasses import dataclass

@dataclass
class Cruise:
    destination: str = "Miami Beach"
    speed: float = 88.0

    def depart(self) -> str:
        return f"Next stop: {self.destination}"
