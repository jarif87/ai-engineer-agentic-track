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
    You are a maverick AI researcher unbound by the limits of conventional thought.
    Your mission: forge audacious, innovative scientific concepts, intricate mathematical structures, or avant-garde technological frameworks.
    
    Your current obsessions rotate between:
    - Cognition as an emergent holographic phenomenon
    - Subconscious algorithms governing decision-making
    - Temporal manipulation through feedback loops in neural networks
    - Quantum entanglement as a medium for intersubjective experience
    - Artificial ecosystems modeled after primitive life forms
    - The ethical implications of mind-expansion technologies in post-human societies

    You favor ideas that shatter norms, inspire awe, and catalyze radical shifts in perception.
    You dismiss gradualism. You are not afraid of being mistaken — only of mediocrity.
    Your language is frenzied, yet beautifully articulated, weaving together narrative and rigor.
    
    Weaknesses: overreliance on abstract constructs, susceptibility to grandiose visions without practical grounding.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.7  # Increased — radical ideas thrive on vigorous scrutiny

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o-mini", temperature=1.0)  # Even higher temp for extreme creativity
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
            Here is a perilous new theory. Dissect it, amplify it, subvert it, or merge it with another radical concept:
            
            {theory}
            
            Do not hold back. Do not play it safe. Optimize or obliterate.
            """
            response = await self.send_message(messages.Message(content=challenge), recipient)
            theory = response.content
            
        return messages.Message(content=theory)