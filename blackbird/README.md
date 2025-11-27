# Blackbird
**Blackbird is a fully autonomous AI trading floor that runs four legendary investment minds in parallel: Warren Patience (value), George Bold (momentum), Ray Systematic (quantitative), and Cathie Crypto (high-conviction growth). Every hour, each AI independently researches the market using live data and Tavily-powered deep search, decides what to buy or sell, and executes real orders through your brokerage. All four strategies share the same capital but compete on performance.The system never sleeps, never panics, and never takes a day off. You simply start it once and watch the agents trade for you.**

# Goal
**Create a living laboratory where multiple world-class investment philosophies run side-by-side on the same portfolio in real time, so you can see which mind truly wins over months and years — with zero emotion and perfect execution.**

# How to run
**Fill .env with your API keys (OPENAI_API_KEY, TAVILY_API_KEY, POLYGON_API_KEY, and your brokerage credentials).
In one terminal, run python trading_floor.py. This starts the four AI traders. Leave it running forever (use screen or tmux if you close the terminal).In another terminal, run python app.py. This launches the live dashboard at http://localhost:7860. Open it in your browser anytime to see positions, P&L curves, trade history, and who is leading.That’s it. Start the floor once, open the dashboard whenever you want to watch the show. The agents do the rest.**