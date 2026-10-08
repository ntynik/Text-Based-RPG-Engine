from dataclasses import dataclass
import openai
from config import API_KEY

@dataclass
class GenerationSettings:
    model_id: str
    temperature: float

@dataclass
class LLMResponse:
    content: str
    total_tokens: int

client = openai.OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY,
)

def generate_response(messages: list[dict[str, str]], settings: GenerationSettings) -> LLMResponse | None:
    try:
        response = client.chat.completions.create(
            model=settings.model_id,
            temperature=settings.temperature,
            messages=messages,
        )

        result = LLMResponse(
            content=response.choices[0].message.content,
            total_tokens=response.usage.total_tokens,
        )

        return result

    except openai.APIConnectionError as e:
        print("Could not connect to the API.")
        print(e.__cause__)
        return None

    except openai.APIStatusError as e:
        print(f"The API returned an error: {e.status_code}\n")
        print(e.response)
        return None

