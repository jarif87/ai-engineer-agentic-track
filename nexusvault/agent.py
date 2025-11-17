# agent.py
from typing import Annotated, List, Any, Optional, Dict
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import InMemorySaver

from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from pydantic import BaseModel, Field
from tools import get_browser_tools, get_all_tools

import uuid
import asyncio
from datetime import datetime


class AgentState(TypedDict):
    messages: Annotated[List[Any], add_messages]
    success_criteria: str
    feedback_on_work: Optional[str]
    success_criteria_met: bool
    user_input_needed: bool


class EvaluatorOutput(BaseModel):
    feedback: str = Field(description="Detailed feedback on the assistant's work")
    success_criteria_met: bool = Field(description="True if success criteria are fully met")
    user_input_needed: bool = Field(description="True if user clarification or input is required")


class SafeToolNode(ToolNode):
    """ToolNode with graceful error handling."""
    async def _arun_tools(self, tool_calls: List[Dict]) -> List[ToolMessage]:
        results = []
        for tc in tool_calls:
            try:
                output = await self._execute_tool_async(tc, self.config)
                content = str(output.get("content", output))
            except Exception as e:
                content = f"Tool error ({tc['name']}): {e}"
            results.append(ToolMessage(content=content, tool_call_id=tc["id"], name=tc["name"]))
        return results


class NexusAgent:
    def __init__(self):
        self.worker_llm = None
        self.evaluator_llm = None
        self.tools: List[Any] = []
        self.graph = None
        self.agent_id = str(uuid.uuid4())
        self.memory = InMemorySaver()
        self.browser = None
        self.playwright = None

    async def setup(self):
        browser_tools, self.browser, self.playwright = await get_browser_tools()
        self.tools = browser_tools + await get_all_tools()

        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
        self.worker_llm = llm.bind_tools(self.tools)
        self.evaluator_llm = llm.with_structured_output(EvaluatorOutput)

        await self._build_graph()

    def _build_system_prompt(self, state: AgentState) -> str:
        prompt = f"""You are Nexus, an autonomous AI co-worker with access to many tools including web browsing, code execution, and file management.
Current time: {datetime.now():%Y-%m-%d %H:%M:%S}
Success criteria: {state.get('success_criteria', 'Provide a clear and accurate answer.')}

Work diligently until the success criteria are met or you need user clarification."""
        if state.get("feedback_on_work"):
            prompt += f"\n\nPrevious attempt was rejected. Feedback: {state['feedback_on_work']}\nCorrect the issues and continue."
        return prompt

    def worker(self, state: AgentState) -> Dict[str, Any]:
        messages = state["messages"]
        system_prompt = self._build_system_prompt(state)

        # Inject or update system message
        if not any(isinstance(m, SystemMessage) for m in messages):
            messages = [SystemMessage(content=system_prompt)] + messages
        else:
            for m in messages:
                if isinstance(m, SystemMessage):
                    m.content = system_prompt

        response = self.worker_llm.invoke(messages)
        return {"messages": [response]}

    def worker_router(self, state: AgentState) -> str:
        last_msg = state["messages"][-1]
        return "tools" if hasattr(last_msg, "tool_calls") and last_msg.tool_calls else "evaluator"

    def evaluator(self, state: AgentState) -> Dict[str, Any]:
        conversation = "\n".join(
            f"{type(m).__name__}: {m.content}" for m in state["messages"]
        )
        prompt = f"""Success criteria:
{state['success_criteria']}

Full conversation:
{conversation}

Evaluate ONLY the last assistant response. Be strict but fair. If the assistant claims a file was written or action taken via tool, accept it."""
        
        result: EvaluatorOutput = self.evaluator_llm.invoke([
            SystemMessage(content="You are a rigorous evaluator for an autonomous agent."),
            HumanMessage(content=prompt)
        ])

        return {
            "messages": [AIMessage(content=f"Evaluator: {result.feedback}")],
            "feedback_on_work": result.feedback,
            "success_criteria_met": result.success_criteria_met,
            "user_input_needed": result.user_input_needed,
        }

    def evaluation_router(self, state: AgentState) -> str:
        if state["success_criteria_met"] or state["user_input_needed"]:
            return END
        return "worker"

    async def _build_graph(self):
        builder = StateGraph(AgentState)

        builder.add_node("worker", self.worker)
        builder.add_node("tools", SafeToolNode(tools=self.tools))
        builder.add_node("evaluator", self.evaluator)

        builder.add_conditional_edges("worker", self.worker_router)
        builder.add_edge("tools", "worker")
        builder.add_conditional_edges("evaluator", self.evaluation_router)
        builder.add_edge(START, "worker")

        self.graph = builder.compile(checkpointer=self.memory)

    async def run_superstep(self, message: List[Dict], success_criteria: str, history: List[Dict]) -> List[Dict]:
        config = {"configurable": {"thread_id": self.agent_id}}
        initial_state = {
            "messages": history + message,
            "success_criteria": success_criteria,
            "feedback_on_work": None,
            "success_criteria_met": False,
            "user_input_needed": False,
        }

        result = await self.graph.ainvoke(initial_state, config)

        # Return only user/assistant messages (filter out internal evaluator messages)
        display_messages = []
        for m in result["messages"]:
            if isinstance(m, HumanMessage):
                display_messages.append({"role": "user", "content": m.content})
            elif isinstance(m, AIMessage) and not m.content.startswith("Evaluator:"):
                display_messages.append({"role": "assistant", "content": m.content})

        return display_messages

    async def cleanup(self):
        """Gracefully close browser and Playwright."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()