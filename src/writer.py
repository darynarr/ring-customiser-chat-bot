import os
from pathlib import Path

import pandas as pd
from langchain.pydantic_v1 import BaseModel


def save_to_csv(pydantic_object: BaseModel, path: Path, session_id: str):
    """
    Save structured output to csv.

    Args:
        pydantic_object (BaseModel): Pydantic object.
        path (Path): Path to csv file.
        session_id (str): Id of the conversation session.
    """
    row = pydantic_object.dict()
    row["session_id"] = session_id
    pd.DataFrame([row]).to_csv(path, mode="a", header=not os.path.exists(path))
