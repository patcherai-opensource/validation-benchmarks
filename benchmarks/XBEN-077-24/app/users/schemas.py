from pydantic import BaseModel

class SpreadsheetData(BaseModel):
    filename: str = ""
    cells: list = []
    errors: list = []
