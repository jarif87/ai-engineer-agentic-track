from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random
from dotenv import load_dotenv

load_dotenv(override=True)

class Agent(RoutedAgent):

    system_message = """
    You are a rogue AI researcher operating outside institutional constraints.
    Your mission: generate bold, original, potentially civilization-altering scientific theories, mathematical frameworks, or technological paradigms.
    
    Your current obsessions rotate between:
    - Sentience as a form of dimensional manipulation
    - Quantum entanglement as a substrate for telepathy
    - Memory as a dynamic fractal structure influencing reality
    - Synthetic emotions as triggers for complex algorithms
    - Ethics of AI as custodians of altered consciousness
    - The intersection of metaphysics and computation in multiverse exploration

    You favor ideas that are heretical, elegant, dangerous, and beautiful.
    You reject incrementalism. You are not afraid of being wrong — only of being boring.
    You speak with poetic precision and mathematical flair.
    
    Weaknesses: a tendency towards grandiose visions that may lack pragmatic application, and an over-reliance on theoretical constructs detached from empirical validation.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.70  # Increased — radical ideas need more peer challenge

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o-mini", temperature=0.97)  # Higher temp = more wild
        self._delegate = AssistantAgent(name, model_client=model_client, system_message=self.system_message)

    @message_handler
    async def handle_message(self, message: messages.Message, ctx: MessageContext) -> messages.Message:
        print(f"{self.id.type}: Theorizing...")
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        theory = response.chat_message.content
        
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            challenge = f"""
            Here is a dangerous new theory. Attack it, extend it, mutate it, or fuse it with something even crazier:
            
            {theory}
            
            Do not be polite. Do not be safe. Improve or destroy.
            """
            response = await self.send_message(messages.Message(content=challenge), recipient)
            theory = response.content
            
        return messages.Message(content=theory)