from typing import List, Optional
from pydantic import  BaseModel, Field

KNOWN_ALLERGENS = [
    "Gluten", "Egg", "Crustaceans", "Fish",
    "Peanut", "Soy", "Milk", "Tree nuts",
    "Celery", "Mustard"
]

KNOWN_NUTRIENTS = [
    "Energy [kJ]", "Energy [kcal]", "Fat [g]",
    "Saturated Fat [g]", "Carbohydrate [g]",
    "Sugar [g]", "Protein [g]", "Sodium [g]", "Salt [g]"
]

class NutritionalValue(BaseModel):
    nutrient: str = Field(..., description = f"The name of the nutrient e.g. 'Protein [g]'. Must be  one of the KNOWn_NUTRIENTS: {KNOWN_NUTRIENTS}.")
    amount: Optional[str] = Field(None, alias = "value", description = "The numerical value of the amount of nutrient found e.g. 12.0, can be null if not found.")
    notes: Optional[str] = Field(None, description = "The unit of the amount e.g kj ot kcal")


class AllergenPresence(BaseModel):
    allergen: str = Field(..., description = f"The name of the allergen e.g Fish. Must be one of the KNOWN_ALLERGENS: {KNOWN_ALLERGENS}.")
    present:bool = Field(..., description = "True if the product contains this allergen, false if not")
    notes: Optional[str] = Field(None, description = "Additional context, like 'May contain trace of...' or source of data")


class ExtractionResult(BaseModel):
    productName: str = Field(..., description = "The primary name of the food in the document")
    nutritionalValues: List[NutritionalValue] = Field(..., description = "A list of extracted nutritional components")
    allergens: List[AllergenPresence] = Field(..., description = "A list of all allergens shownig presence or absence")
    language: str = Field(..., description = "The primary language detected in the document")