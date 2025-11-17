# tools.py
from playwright.async_api import async_playwright
from langchain_community.agent_toolkits import PlayWrightBrowserToolkit
from langchain_community.tools.wikipedia.tool import WikipediaQueryRun
from langchain_experimental.tools import PythonREPLTool
from langchain_community.utilities import GoogleSerperAPIWrapper, WikipediaAPIWrapper
from langchain.tools import tool
from dotenv import load_dotenv
import os
import requests
from pathlib import Path

load_dotenv(override=True)

# === Pushover credentials (make sure these are set in your .env) ===
PUSHOVER_TOKEN = os.getenv("PUSHOVER_TOKEN")
PUSHOVER_USER = os.getenv("PUSHOVER_USER", os.getenv("PUSHOVER_USER_KEY"))  # supports both!  # ← double-check this name matches your .env
PUSHOVER_URL = "https://api.pushover.net/1/messages.json"

serper = GoogleSerperAPIWrapper()


# ──────────────────────────────────────────────────────────────
# 1. Browser tools (Playwright) – launches visible browser
# ──────────────────────────────────────────────────────────────
async def get_browser_tools():
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(
        headless=False,
        args=["--no-sandbox", "--disable-setuid-sandbox", "--start-maximized"]
    )
    context = await browser.new_context(
        viewport={"width": 1920, "height": 1080},
        java_script_enabled=True,
        bypass_csp=True
    )
    # Hide automation flags
    await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => false});")
    context.set_default_timeout(90_000)

    toolkit = PlayWrightBrowserToolkit.from_browser(async_browser=browser)
    await context.new_page()  # pre-warm
    return toolkit.get_tools(), browser, playwright


# ──────────────────────────────────────────────────────────────
# 2. Pushover notification – now 100% working
# ──────────────────────────────────────────────────────────────
@tool
def send_push_notification(text: str) -> str:
    """Send a push notification to your phone instantly."""
    if not PUSHOVER_TOKEN or not PUSHOVER_USER:
        return "Error: Pushover credentials missing in .env (PUSHOVER_TOKEN / PUSHOVER_USER_KEY)"
    try:
        response = requests.post(
            PUSHOVER_URL,
            data={"token": PUSHOVER_TOKEN, "user": PUSHOVER_USER, "message": text},
            timeout=10
        )
        if response.status_code == 200:
            return f"Push notification sent: {text}"
        else:
            return f"Pushover error {response.status_code}: {response.text}"
    except Exception as e:
        return f"Pushover failed: {str(e)}"


# ──────────────────────────────────────────────────────────────
# 3. Safe & working file tools (replaces buggy langchain ones)
# ──────────────────────────────────────────────────────────────
@tool
def write_markdown_file(filename: str, content: str) -> str:
    """Write or overwrite a markdown (.md) or text file. Creates folders automatically."""
    try:
        path = Path("sandbox") / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return f"File successfully saved: {filename}"
    except Exception as e:
        return f"Write failed: {str(e)}"


@tool
def append_to_file(filename: str, content: str) -> str:
    """Append text to an existing file (or create if missing)."""
    try:
        path = Path("sandbox") / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            f.write(content + "\n")
        return f"Appended to {filename}"
    except Exception as e:
        return f"Append failed: {str(e)}"


# ──────────────────────────────────────────────────────────────
# 4. Other tools
# ──────────────────────────────────────────────────────────────
@tool
def search(query: str) -> str:
    """Google search via Serper."""
    return serper.run(query)


async def get_all_tools():
    """Called by agent.py – returns every tool in one list."""
    browser_tools, _, _ = await get_browser_tools()
    
    wikipedia = WikipediaAPIWrapper()
    wiki_tool = WikipediaQueryRun(api_wrapper=wikipedia)
    python_repl = PythonREPLTool()

    return (
        browser_tools +
        [
            send_push_notification,
            search,
            write_markdown_file,
            append_to_file,
            python_repl,
            wiki_tool
        ]
    )