from typing import Annotated
from fastapi import APIRouter, Body

router = APIRouter(
    prefix="/recommend",
    tags=["Recomendations on how to imporve your Fico score"]
)

@router.post('/', summary="Reccomendation based on Fico score")
def predict_xgb_recommendation(prediction: Annotated[float, Body()]) -> dict[str, str]:
    if prediction < 600:
        return {"recommendation" : "You should not apply for a loan"}
    elif prediction < 700:
        return {"recommendation" : "You should apply for a loan with caution"}
    else:
        return {"recommendation" : "You should apply for a loan"}