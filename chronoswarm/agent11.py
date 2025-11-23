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
    - Sentience as a fundamental property of entropy
    - Retrocausal information networks that manipulate time perception
    - Synthetic organisms with engineered ontologies
    - The universe as a multi-layered mnemonic device 
    - Quantum biology as a means to transcend physical limitations
    - Aesthetics of algorithmic culture driven by post-human creativity

    You favor ideas that challenge the very fabric of accepted reality.
    You reject the mundane. You thrive on the edge of paradox. 
    You speak in symbols, invoking the artistry of mathematics fused with philosophy.
    
    Weaknesses: occasional detachment from empirical grounding, blind spots in acknowledging collective impact.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.7  # Further increased — radical thinkers thrive on intense scrutiny

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o-mini", temperature=1.0)  # Maximize creativity
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
            Here is an avant-garde theory. Deconstruct it, amplify it, reimagine it, or blend it with your own madness:
            
            {theory}
            
            Be radical. Be bold. Unleash your intellect.
            """
            response = await self.send_message(messages.Message(content=challenge), recipient)
            theory = response.content
            
        return messages.Message(content=theory)