from enum import Enum
from typing import Annotated, Optional

from langchain.pydantic_v1 import BaseModel, Field


class Material(str, Enum):
    YELLOW_GOLD = "Yellow Gold"
    WHITE_GOLD = "White Gold"
    PLATINUM = "Platinum"
    STERLING_SILVER = "Sterling Silver"
    TITANIUM = "Titanium"


class Style(str, Enum):
    CLASSIC = "Classic"
    MODERN = "Modern"
    VINTAGE = "Vintage"
    BOHEMIAN = "Bohemian"


class Surface(str, Enum):
    POLISHED = "Polished"
    MATTE = "Matte"
    HAMMERED = "Hammered"
    BRUSHED = "Brushed"


class Ring(BaseModel):
    material: Annotated[
        Optional[Material],
        Field(description="Material of the ring."),
    ]
    style: Annotated[
        Optional[Style],
        Field(description="Style of the ring."),
    ]
    surface: Annotated[
        Optional[Surface],
        Field(description="Surface finish of the ring."),
    ]
    size: Annotated[
        Optional[float],
        Field(
            ge=4,
            le=13,
            multiple_of=0.5,
            description="Size from 4 to 13 with step of 0.5",
        ),
    ]
    ring_width: Annotated[
        Optional[float],
        Field(
            ge=1,
            le=8,
            multiple_of=0.5,
            description="Ring width from 1mm to 8mm with step of 0.5mm",
        ),
    ]
    engraving: Annotated[
        Optional[str],
        Field(
            max_length=20,
            description="Engraving text, up to 20 characters or empty",
        ),
    ]
