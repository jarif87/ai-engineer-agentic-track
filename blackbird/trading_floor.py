from traders import Trader
from typing import List
import asyncio
from tracers import LogTracer
from agents import add_trace_processor
from market import is_market_open
from dotenv import load_dotenv
import os

load_dotenv(override=True)

RUN_EVERY_N_MINUTES = int(os.getenv("RUN_EVERY_N_MINUTES", "60"))
RUN_EVEN_WHEN_MARKET_IS_CLOSED = True

# Only OpenAI models
names = ["Warren", "George", "Ray", "Cathie"]
lastnames = ["Patience", "Bold", "Systematic", "Crypto"]

model_names = [
    "gpt-4o-mini",
    "gpt-4.1-nano",
    "o3-mini",
    "o4-mini",
]


short_model_names = [
    "GPT-4o-mini",
    "GPT-4.1-nano",
    "o3-Mini",
    "o4-Mini",
]


def create_traders() -> List[Trader]:
    traders = []
    for name, lastname, model in zip(names, lastnames, model_names):
        traders.append(Trader(name, lastname, model))
    return traders


async def run_every_n_minutes():
    add_trace_processor(LogTracer())
    traders = create_traders()
    
    print(f"Starting scheduler: {', '.join(f'{n} {ln} ({m})' for n, ln, m in zip(names, lastnames, short_model_names))}")
    print(f"Running every {RUN_EVERY_N_MINUTES} minutes\n")

    while True:
        if RUN_EVEN_WHEN_MARKET_IS_CLOSED or is_market_open():
            print(f"Running traders @ {asyncio.get_event_loop().time():.0f}")
            await asyncio.gather(*[trader.run() for trader in traders])
        else:
            print("Market is closed, skipping this cycle")
        
        await asyncio.sleep(RUN_EVERY_N_MINUTES * 60)


if __name__ == "__main__":
    asyncio.run(run_every_n_minutes())