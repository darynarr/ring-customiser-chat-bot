import math
from decimal import Decimal
from enum import Enum
from typing import Annotated, Optional, Union

import numpy as np
from langchain.pydantic_v1 import BaseModel, Field, validator


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


def round_step_size(quantity: Union[float, Decimal], step_size: Union[float, Decimal]) -> float:
    """Rounds a given quantity to a specific step size
    :param quantity: required
    :param step_size: required
    :return: decimal
    """
    precision: int = int(round(-math.log(step_size, 10), 0))
    return float(round(quantity, precision))


class Ring(BaseModel):
    """
    Ring schema.
    """

    material: Annotated[
        Material,
        Field(description="Material of the ring."),
    ]
    style: Annotated[
        Style,
        Field(description="Style of the ring."),
    ]
    surface: Annotated[
        Surface,
        Field(description="Surface finish of the ring."),
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
        Field(
            max_length=20,
            description="Engraving text, up to 20 characters or empty",
        ),
    ]

    @validator("size", pre=True)
    def check_size(cls, value):
        # Clip values outside of the range
        value = np.clip(value, 4, 13)

        step_size = 0.5
        if value % step_size == 0:
            return value
        # Ceil size if needed
        return value + (step_size - value % step_size)

    @validator("ring_width", pre=True)
    def check_ring_width(cls, value):
        # Cast to float if needed
        if isinstance(value, str):
            value = float(value.replace("mm", "").strip())

        # Clip value outside of the range
        value = np.clip(value, 1, 8)
        step_size = 0.5
        if value % step_size == 0:
            return value
        # Round if needed
        return round_step_size(value, step_size=step_size)

    @validator("engraving", pre=True)
    def check_engraving(cls, value):
        if value == "" or value is None:
            return None
        return str(value)[:20]
