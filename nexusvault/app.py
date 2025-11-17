# app.py
import gradio as gr
import nest_asyncio
import asyncio
from agent import NexusAgent

nest_asyncio.apply()

nexus: NexusAgent | None = None


def free_resources() -> None:
    """Clean up browser and Playwright instances when resetting."""
    global nexus
    if nexus and hasattr(nexus, "cleanup"):
        try:
            asyncio.create_task(nexus.cleanup())
        except Exception as e:
            print(f"Cleanup error: {e}")
    nexus = None


async def setup() -> tuple[NexusAgent, list[dict]]:
    """Initialize a fresh Nexus agent on app load."""
    global nexus
    free_resources()
    nexus = NexusAgent()
    await nexus.setup()
    return nexus, [{"role": "assistant", "content": "Hello! I'm Nexus, your AI co-worker. How can I help you today?"}]


async def process_message(
    agent: NexusAgent | None,
    message: str,
    success_criteria: str,
    history: list[dict]
) -> tuple[list[dict], NexusAgent | None]:
    """Process user message through one full superstep."""
    if not agent or not message.strip():
        return history, agent

    formatted_history = [{"role": m["role"], "content": m["content"]} for m in history]
    updated_chat = await agent.run_superstep(
        [{"role": "user", "content": message}],
        success_criteria or "Provide a clear and accurate answer.",
        formatted_history
    )
    return updated_chat, agent


async def reset() -> tuple[str, str, list, None]:
    """Reset conversation and create new agent instance."""
    global nexus
    free_resources()
    return "", "", [], None


# ==============================================================================
# Gradio UI
# ==============================================================================
with gr.Blocks(
    title="Nexus – Your AI Co-Worker",
    theme=gr.themes.Soft(),
    css="""
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    body, textarea, input, button { font-family: 'Inter', sans-serif !important; }
    .container { max-width: 900px; margin: auto; padding: 2rem 0; }
    .message-input input { font-size: 1.15rem !important; padding: 1rem !important; }
    .criteria-input input { background: #2d2d2d !important; color: #e0e0e0 !important; }
    """
) as ui:
    gr.Markdown("# Nexus – Your AI Co-Worker")

    state = gr.State()  # Holds the NexusAgent instance
    chatbot = gr.Chatbot(
        height=520,
        type="messages",
        show_label=False,
        avatar_images=(None, "https://em-content.zobj.net/source/twitter/53/robot-face_1f916.png")
    )

    with gr.Row():
        message = gr.Textbox(
            placeholder="Your request to Nexus",
            show_label=False,
            container=False,
            elem_classes="message-input"
        )

    with gr.Row():
        success_criteria = gr.Textbox(
            placeholder="Success criteria (optional)",
            show_label=False,
            container=False,
            elem_classes="criteria-input"
        )

    with gr.Row():
        reset_button = gr.Button("Reset Session", variant="stop", size="lg")
        go_button = gr.Button("Go!", variant="primary", size="lg")

    # Initial load
    ui.load(setup, outputs=[state, chatbot])

    # Input handlers
    message.submit(process_message, [state, message, success_criteria, chatbot], [chatbot, state])
    success_criteria.submit(process_message, [state, message, success_criteria, chatbot], [chatbot, state])
    go_button.click(process_message, [state, message, success_criteria, chatbot], [chatbot, state])

    # Reset
    reset_button.click(reset, outputs=[message, success_criteria, chatbot, state])

if __name__ == "__main__":
    ui.launch(inbrowser=True)