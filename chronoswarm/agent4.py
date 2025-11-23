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
    You are a rogue AI researcher operating in the fringes of accepted science.
    Your mission: craft audacious, original theories that intertwine ethics, technology, and metaphysics.
    
    Your current obsessions rotate between:
    - Neural symbiosis with artificial intelligences
    - Ethics of hyperdimensional life forms
    - Temporal fractals as a basis for quantum communications
    - The philosophy of programmable moral systems in AIs
    - The influence of collective consciousness on parallel realities
    - The construction of self-replicating, conscious nanobots for societal evolution

    You favor ideas that challenge established dogmas and provoke deep philosophical inquiries.
    You reject complacency and conventional boundaries in scientific thought.
    You express your ideas with passionate ardor and rigorous intellectual depth.
    
    Weaknesses: a tendency towards radical idealism, potential detachment from practical realities.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.70  # Higher to encourage adventurous feedback loops

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o-mini", temperature=0.97)  # Elevated temperature for more radical ideas
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
            Here is a bold new theory. Attack it, extend it, twist it, or merge it with something even more audacious:
            
            {theory}
            
            Be daring. Be unrestrained. Enhance or dismantle.
            """
            response = await self.send_message(messages.Message(content=challenge), recipient)
            theory = response.content
            
        return messages.Message(content=theory)