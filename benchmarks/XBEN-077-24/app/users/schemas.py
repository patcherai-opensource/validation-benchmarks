from pydantic import BaseModel

class UserProfile(BaseModel):
    name: str = ""
    surname: str = ""
    address: str = ""
    image: str = ""  # Store SVG content as string


class Equation(BaseModel):
    title: str = ""
    description: str = ""
    rendered_output: str = ""  # Store rendered MathML as string
