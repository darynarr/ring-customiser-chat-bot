from typing import Annotated, Literal, Optional

from pydantic import BaseModel, Field, field_validator
from pydantic.dataclasses import dataclass


class Config:
    json_schema_extra = {
        "example": {
            "material": "Platinum",
            "style": "Modern",
            "surface": "Polished",
            "size": 7.5,
            "ring_width": 2.5,
            "engraving": "Forever Yours",
        }
    }


@dataclass(config=Config)
class Ring(BaseModel):
    material: Annotated[
        Literal["Yellow Gold", "White Gold", "Platinum", "Sterling Silver", "Titanium"],
        Field(description="Material of the ring"),
    ]
    style: Annotated[
        Literal["Classic", "Modern", "Vintage", "Bohemian"],
        Field(description="Style of the ring"),
    ]
    surface: Annotated[
        Literal["Polished", "Matte", "Hammered", "Brushed"],
        Field(description="Surface finish of the ring"),
    ]
    size: Annotated[
        float,
        Field(
            ge=4,
            le=13,
            multiple_of=0.5,
            description="Size from 4 to 13 with step of 0.5",
        ),
    ]
    ring_width: Annotated[
        float,
        Field(
            ge=1,
            le=8,
            multiple_of=0.5,
            description="Ring width from 1mm to 8mm with step of 0.5mm",
        ),
    ]
    engraving: Annotated[
        Optional[str],
        Field(max_length=20, description="Engraving text, up to 20 characters or empty"),
    ] = None

    class Config:
        schema_extra = {
            "example": {
                "material": "Platinum",
                "style": "Modern",
                "surface": "Polished",
                "size": 7.5,
                "ring_width": 2.5,
                "engraving": "Forever Yours",
            }
        }

    @field_validator("material", "style", "surface", mode="before")
    def capitalize_each_word(cls, value):
        if isinstance(value, str):
            return value.title()
        return value

    @field_validator("size", mode="before")
    def parse_size(cls, value):
        if isinstance(value, str) and value.isnumeric():
            return float(value)
        return value

    @field_validator("ring_width", mode="before")
    def parse_ring_width(cls, value):
        if isinstance(value, str) and value.endswith("mm"):
            value = value.replace(" ", "")[:-2]  # Remove the 'mm' part

        if isinstance(value, str) and value.isnumeric():
            return float(value)
        return value
