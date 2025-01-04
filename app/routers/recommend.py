from typing import Annotated
from fastapi import APIRouter, Body
from app.schemas.user import UserData
from app.services.feature_importance import FeatureRecommender

router = APIRouter(
    prefix="/recommend", tags=["Recomendations on how to imporve your Fico score"]
)


@router.post("/", summary="Reccomendation based on Fico score")
def predict_xgb_recommendation(data: Annotated[UserData, Body()]):
    user_data = data.model_dump()

    recommender = FeatureRecommender(data.model_dump().keys())
    recommendations = recommender.analyze_features(user_data)

    return recommendations
