from pydantic import BaseModel, Field

from perfume_gender.config import MAX_ACCORDS


class AccordInput(BaseModel):
    name: str = Field(min_length=1, max_length=40, examples=["woody"])
    intensity: float = Field(gt=0, le=100, description="Intensidad relativa 0-100", examples=[80])


class PredictRequest(BaseModel):
    accords: list[AccordInput] = Field(min_length=1, max_length=MAX_ACCORDS)

    model_config = {
        "json_schema_extra": {
            "example": {"accords": [
                {"name": "woody", "intensity": 100},
                {"name": "fresh spicy", "intensity": 70},
                {"name": "aromatic", "intensity": 55},
            ]}
        }
    }


class Influence(BaseModel):
    accord: str
    effect: dict[str, float]
    pushes_toward: str


class PredictResponse(BaseModel):
    label: str
    probabilities: dict[str, float]
    accords_used: dict[str, float]
    influences: list[Influence]
