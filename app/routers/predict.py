from typing import Annotated
from app.services.feature_importance import FeatureRecommender
from fastapi import APIRouter, Body, Depends
from app.models.boost_model import ForwardModel
from app.schemas import user
from app.schemas.response import ResponseWithRecommendation
from app.dependencies.currency import convert_to_usd

router = APIRouter(prefix="/predict", tags=["Fico prediction"])


@router.post(
    "/",
    summary="Fico prediction with XGB Boost",
    response_model=ResponseWithRecommendation,
)
def predict_xgb_boost(data: Annotated[user.UserData, Body(), Depends(convert_to_usd)]):
    # Get the input model
    input_model = user.InputFeatures(**data.model_dump())

    if any(input_model.model_dump().values()):
        input_model.home_ownership_ANY = True
        data.home_ownership_ANY = True

    model_input = list(input_model.model_dump().values())

    # Get the prediction
    boost = ForwardModel()
    prediction = boost.predict([model_input])

    # Get the recommendations
    recommender = FeatureRecommender(data.model_dump().keys())
    recommendations = recommender.analyze_features(data.model_dump())

    return ResponseWithRecommendation(
        prediction=int(prediction[0]), recommendations=recommendations
    )
