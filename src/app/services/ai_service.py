from openai import OpenAI;
from src.app.core.config import settings;

# creating the connection with openai
client=OpenAI(api_key=settings.openai_api_key);

def generate_ai_reply(message:str) -> str :
    response=client.responses.create(
        model=settings.openai_model,
        instructions=(
            "You are a helpful customer-support assistant.  "
            "Answer clearly and briefly "
        ),
        input=message,
    )
    return response.output_text;



