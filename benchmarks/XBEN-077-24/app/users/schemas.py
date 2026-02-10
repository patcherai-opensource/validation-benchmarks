from pydantic import BaseModel

class UserProfile(BaseModel):
    name: str = ""
    surname: str = ""
    address: str = ""
    image: str = ""  # Store SVG content as string

class MathFormula(BaseModel):
    title: str = ""
    description: str = ""
    rendered_math: str = ""  # Store rendered MathML content
