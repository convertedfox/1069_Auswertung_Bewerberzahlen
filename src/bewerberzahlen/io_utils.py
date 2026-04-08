from __future__ import annotations

from io import BytesIO

import pandas as pd


def read_excel_from_bytes(content: bytes) -> pd.DataFrame:
    return pd.read_excel(BytesIO(content), engine="openpyxl")


def dataframe_to_excel_bytes(df: pd.DataFrame) -> bytes:
    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    return buffer.getvalue()
