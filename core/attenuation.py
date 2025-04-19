
"""Regional ML attenuation model."""
import math
from dataclasses import dataclass

@dataclass
class AttenuationModel:
    logA0: float = -1.3
    gamma: float = 1.0
    kappa: float = 0.003

    def ml_to_amp(self, ml: float, r_km: float) -> float:
        # logA = ML + logA0 - gamma*log10(r) - kappa*r
        return 10 ** (ml + self.logA0 - self.gamma*math.log10(r_km) - self.kappa*r_km)
