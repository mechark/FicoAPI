from typing import Tuple
from pydantic import BaseModel

class FeatureStatus(BaseModel):
    can_improve: bool = True
    is_negative: bool = False

class FeatureConfig(BaseModel):
    """Configuration for a feature including its threshold and Ukrainian translation."""

    threshold: Tuple[float, float]
    ukrainian_name: str
    explanation: str
    status: FeatureStatus = FeatureStatus()