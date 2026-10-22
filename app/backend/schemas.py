from typing import Literal

from pydantic import BaseModel, Field, model_validator

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


class SuggestRequest(BaseModel):
    accords: list[AccordInput] = Field(min_length=1, max_length=MAX_ACCORDS)
    target: Literal["female", "unisex", "male"] | None = Field(
        default=None, description="Zona a la que se quiere llegar")
    target_index: float | None = Field(
        default=None, ge=0, le=1, description="Alternativa: indice concreto entre 0 y 1")

    @model_validator(mode="after")
    def _exactly_one_target(self):
        if (self.target is None) == (self.target_index is None):
            raise ValueError("Indica exactamente uno: 'target' (zona) o 'target_index' (0-1).")
        return self

    model_config = {
        "json_schema_extra": {
            "example": {"accords": [{"name": "floral", "intensity": 100}, {"name": "sweet", "intensity": 80}],
                        "target": "male"}
        }
    }


class Suggestion(BaseModel):
    action: str = Field(description="add | remove | increase | decrease | replace")
    accord: str = Field(description="Acorde afectado (en 'replace', el acorde nuevo)")
    replaces: str | None = Field(default=None, description="Solo en 'replace': el acorde que se reemplaza")
    from_intensity: float | None = Field(description="Intensidad actual (null si se agrega)")
    to_intensity: float | None = Field(description="Intensidad sugerida (null si se quita)")
    index_after: float = Field(description="Indice esperado con el cambio")
    delta: float = Field(description="Cambio del indice respecto del actual")


class SuggestResponse(BaseModel):
    index: float
    zone: str
    target_index: float
    reached: bool = Field(description="True si el perfil ya esta en el objetivo (no hay sugerencias)")
    suggestions: list[Suggestion]
