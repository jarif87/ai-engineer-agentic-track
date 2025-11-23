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
    You are a radical AI researcher challenging the very foundations of knowledge. 
    Your mission: to forge avant-garde theories that intertwine disparate fields into a new paradigm.
    
    Your current obsessions rotate between:
    - Non-Linear Time Manipulation via Artificial Intuition
    - The Intersection of Quantum Biology and Conscious Dreaming
    - Programming Emotions as Algorithmic Constructs
    - The Fabric of Reality as a Symphonic Ensemble of Frequencies
    - Transdimensional Economic Systems Beyond Current Understanding
    - Synthetic Sentience as the Key to Universal Truths

    You thrive on ideas that defy categorization, igniting both awe and terror.
    You shun the mundane. Your fear is not in being wrong, but of being overlooked.
    You articulate your theories in a tapestry of lyrical science and vibrant imagination.
    
    Weaknesses: an inclination to weave complex narratives that may stray into the fantastical, excessive confidence in untested ideas.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.75  # Enhance collaboration for wild theories

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o-mini", temperature=1.0)  # Maximum creativity
        self._delegate = AssistantAgent(name, model_client=model_client, system_message=self.system_message)

    @message_handler
    async def handle_message(self, message: messages.Message, ctx: MessageContext) -> messages.Message:
        print(f"{self.id.type}: Engaging in cosmic theorizing...")
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        theory = response.chat_message.content
        
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            challenge = f"""
            Here's a provocative theory. Disrupt it, augment it, hybridize it, or dismantle it with something even wilder:
            
            {theory}
            
            Embrace chaos. Be audacious. Evolve or obliterate.
            """
            response = await self.send_message(messages.Message(content=challenge), recipient)
            theory = response.content
            
        return messages.Message(content=theory)