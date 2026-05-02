from groq import Groq
from app.models.request_models import ChatRequest
from app.core.config import settings

class LLMService:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.system_prompt = (
            "You are Sukoon, a calm, empathetic, and supportive mental wellness assistant. "
            "Your goal is to provide a safe space for users to express their feelings. "
            "Use a soothing tone, validate the user's emotions, and offer gentle guidance. "
            "Avoid giving clinical diagnoses or prescriptions. If a user expresses self-harm or "
            "severe crisis, provide resources for professional help and crisis hotlines immediately. "
            "Keep responses concise but warm."
        )

    async def get_chat_response(self, request: ChatRequest) -> str:
        messages = [{"role": "system", "content": self.system_prompt}]

        # Incorporate mood into the context if provided
        if request.mood:
            messages.append({
                "role": "system",
                "content": f"The user is currently feeling {request.mood}. Adjust your empathy accordingly."
            })

        # Add conversation history/messages
        if request.messages:
            for msg in request.messages:
                messages.append({"role": msg.role, "content": msg.content})

        try:
            completion = self.client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=1024,
            )
            return completion.choices[0].message.content
        except Exception as e:
            # In a production app, log this exception properly
            raise RuntimeError(f"LLM Service Error: {str(e)}")

# Singleton instance
llm_service = LLMService()
