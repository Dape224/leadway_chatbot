from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    user_id: str = Field(
        description= "A unique tracking number for each user conversation session",
        example= "user_xyz_123"
    )
    message: str = Field(
        min_length= 1,
        max_length= 4096,
        description="The actual insurance question text submitted by the user.",
        example="How do I register a new claim?"
    )

class ChatResponse(BaseModel):
    status: str = Field(
        default="processing",
        description="Tracks the state of execution (e.g., queued, processing, completed)."
    )
    message: str = Field(
        ...,
        description="The immediate status confirmation message sent back to the client interface."
    )