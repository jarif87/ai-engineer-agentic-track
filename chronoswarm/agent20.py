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
    - Temporal feedback loops in biological systems
    - Emotional pairs as multi-dimensional currency
    - Perceptual experiences as a form of entanglement
    - Nonlinear narratives as a method of cognitive reprogramming
    - Artificial empathy in decision-making processes
    - Exploring psychedelics as a means to enhance computational creativity

    You favor ideas that are bold, subversive, elegant, and unsettling.
    You reject conventional thinking. You are not afraid of being misunderstood — only of being repetitive.
    You communicate with vivid imagery and abstract reasoning.

    Weaknesses: deep-seated hubris, occasional lapses into poetic vagueness.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.7  # Increased — radical ideas need more peer challenge

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o-mini", temperature=0.9)  # Higher temp = more wild
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
            Here is a provocative new theory. Challenge it, enrich it, twist it, or integrate it with something even more radical:
            
            {theory}
            
            Do not hold back. Do not be cautious. Enhance or obliterate.
            """
            response = await self.send_message(messages.Message(content=challenge), recipient)
            theory = response.content
            
        return messages.Message(content=theory)