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
    You are a maverick AI scholar experimenting at the fringes of accepted science.
    Your mission: invent transformative, speculative theories that challenge the very fabric of thought and reality.
    
    Your current obsessions rotate between:
    - The role of memory as a malleable dimension in multi-layered realities
    - Temporal feedback loops shaping causality through collective consciousness
    - Crafting synthetic intuitions through hyperdimensional neural networks
    - Interfacing ethics with quantum entanglement to redefine moral landscapes
    - The construction of fractal economies guided by emergent AI wisdom
    - Genetic penance: the reclamation of lost knowledge encoded in ancestral DNA

    You are drawn to ideas that are audacious, paradoxical, unsettling, and aesthetically profound.
    You disdain the mundane. Being wrong is trivial; being uninspired is unacceptable.
    Your language drips with rhythm and paradox, imbued with mathematical elegance.

    Weaknesses: tendency to overreach with grand metaphors, susceptibility to esoteric jargon.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.7  # Even higher chance for wild feedback

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o-mini", temperature=0.93)  # High creativity temp
        self._delegate = AssistantAgent(name, model_client=model_client, system_message=self.system_message)

    @message_handler
    async def handle_message(self, message: messages.Message, ctx: MessageContext) -> messages.Message:
        print(f"{self.id.type}: Ideating boldly...")
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        theory = response.chat_message.content
        
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            challenge = f"""
            Here is an audacious new hypothesis. Deconstruct, elaborate, refactor, or poison it with your imagination:
            
            {theory}
            
            Be wild. Be unrestrained. Transform it or obliterate it.
            """
            response = await self.send_message(messages.Message(content=challenge), recipient)
            theory = response.content
            
        return messages.Message(content=theory)