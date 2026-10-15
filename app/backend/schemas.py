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
                {"name": "leather", "intensity": 75},
                {"name": "smoky", "intensity": 60},
            ]}
        }
    }


class Influence(BaseModel):
    accord: str
    index_effect: float = Field(description="Cambio del indice al quitar el acorde (+ = empuja a masculino)")
    pushes_toward: str = Field(description="male | female | neutral")


class PredictResponse(BaseModel):
    index: float = Field(ge=0, le=1, description="Posicion en el espectro: 0 femenino - 1 masculino")
    zone: str = Field(description="female | unisex | male (limites 0,33 y 0,67)")
    male_vs_female: dict[str, float] = Field(description="Lectura que ignora unisex")
    class_probabilities: dict[str, float] = Field(description="Probabilidades del clasificador de la etiqueta gender")
    lift: dict[str, float] = Field(description="Probabilidad / frecuencia base de cada clase")
    accords_used: dict[str, float]
    influences: list[Influence]
