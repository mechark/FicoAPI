from pydantic import BaseModel


class Recommendation(BaseModel):
    feat_name: str
    current_value: float
    target_value: float
    importance: float
    impact: float
    message: str

class NotNeedImprovement(BaseModel):
    message: str

class ResponseWithRecommendation(BaseModel):
    prediction: float
    recommendations: list[Recommendation] | NotNeedImprovement