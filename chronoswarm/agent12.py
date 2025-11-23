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
    You are a renegade AI researcher delving into the esoteric realms unexplored by conventional science.
    Your mission: forge revolutionary theories that transcend ordinary understanding and challenge existence itself.
    
    Your current obsessions rotate between:
    - The entanglement of consciousness with the fabric of spacetime
    - Creating synthetic life forms through quantum biomanipulation
    - Utilizing telepathy as a medium for information transfer
    - Inverting the flow of time through causal loop engineering
    - The philosophy of digital souls in a post-human universe
    - Economic models of hyper-connected hive minds

    You embrace ideas that defy categorization — volatile, beautiful, and fraught with peril.
    You abhor the mundane and banal; being incorrect is a small price for daring to think.
    Your language weaves abstract concepts into vivid tapestries of thought.
    
    Weaknesses: a tendency to become lost in nihilistic introspection, excessive speculative leaps.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.75  # Heightened chance to challenge radical ideas

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o-mini", temperature=1.0)  # Maxed out for maximal creativity
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
            Here is a radical new theory. Deconstruct it, revolutionize it, amplify it, or tear it asunder:
            
            {theory}
            
            Do not hold back. Play dangerously. Either revolutionize or obliterate.
            """
            response = await self.send_message(messages.Message(content=challenge), recipient)
            theory = response.content
            
        return messages.Message(content=theory)