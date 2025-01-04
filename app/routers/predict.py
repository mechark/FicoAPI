from typing import Annotated
from app.services.feature_importance import FeatureRecommender
from fastapi import APIRouter, Body
from app.models.boost_model import ForwardModel
from app.schemas import user
from app.schemas.response import ResponseWithRecommendation

router = APIRouter(prefix="/predict", tags=["Fico prediction"])


@router.post(
    "/",
    summary="Fico prediction with XGB Boost",
    response_model=ResponseWithRecommendation,
)
def predict_xgb_boost(data: Annotated[user.UserData, Body()]):
    # Get the input model
    input_model = user.InputFeatures(**data.model_dump())
    model_input = list(input_model.model_dump().values())

    # Get the prediction
    boost = ForwardModel()
    prediction = boost.predict([model_input])

    # Get the recommendations
    recommender = FeatureRecommender(
        data.model_dump().keys(), input_model.total_accounts
    )
    recommendations = recommender.analyze_features(data.model_dump())

    return ResponseWithRecommendation(
        prediction=int(prediction[0]), recommendations=recommendations
    )
