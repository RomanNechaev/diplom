from dataclasses import dataclass


@dataclass
class ExperimentResult:
    name: str
    proc: float
    mse: float
    ssim: float
    lpips: float
