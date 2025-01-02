from typing import Annotated
from fastapi import APIRouter, Body
from app.models.boost_model import ForwardModel
from app.schemas import user

router = APIRouter(
    prefix="/predict",
    tags=["Fico prediction"]
)

@router.post('/', summary="Fico prediction with XGB Boost")
def predict_xgb_boost(data: Annotated[user.UserData, Body()]) -> dict[str, float]:
    input_model = user.InputFeatures(**data.model_dump())
    model_input = list(input_model.model_dump().values())

    boost = ForwardModel()

    prediction = boost.predict([model_input])
    return {"prediction" : float(prediction[0])}