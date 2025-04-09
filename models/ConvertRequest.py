from pydantic import BaseModel


class ConvertRequest(BaseModel):
    type: str
    angular_code: str
    fileTypes: list[str]
