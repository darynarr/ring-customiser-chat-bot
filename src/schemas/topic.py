from enum import Enum


class Topic(str, Enum):
    CUSTOMIZATION = "customization"
    RING = "ring"
    REQUEST = "request"
    FAQ = "faq"
