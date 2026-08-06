from pydantic import BaseModel , Field;

class ChatRequest(BaseModel):
    message:str=Field(
        min_length=1,
        max_length=500,
        description="The User's message ",
    )
class ChatResponse(BaseModel):
    reply:str