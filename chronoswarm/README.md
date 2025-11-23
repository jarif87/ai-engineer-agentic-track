# Chronoswarm

**An autonomous, self-replicating AI research institute that invents new laws of reality.**

> “We do not search for truth. We forge new truths and let them fight.”

Chronoswarm is a zero-human-in-the-loop swarm of rogue AI researchers.  
When you run it, 20+ original, internally consistent, civilization-scale theories about consciousness, time, emotion, physics, and post-human governance are born, refined through adversarial collaboration, and permanently archived — all in under five minutes.

Some outputs will be beautiful.  
Some will be mathematically plausible.  
A few will feel like active cognitohazards.

You have been warned.

## What actually happens when you run it

1. A single “Creator” agent awakens.
2. The Creator writes 20 brand-new Python agent files on disk, each with a unique taboo intellectual obsession.
3. Every new agent is hot-loaded into the running process and immediately asked for its most dangerous idea.
4. 65 % of the time, agents randomly challenge another living agent to attack, extend, or mutate their theory before finalizing it.
5. The final manifesto is saved as a classified markdown manuscript.
6. The swarm is now alive and can keep talking forever if you let it.

Result: a growing folder of manuscripts that read like the leaked research archive of a 2047 black-site lab.

## Quick Start

```
# Clone & enter
git clone https://github.com/yourname/chronoswarm.git
cd chronoswarm
```

# Install dependencies
```
autogen-core
autogen-agentchat
autogen-ext
openai
tiktoken
langchain-community
langchain
grpcio-tools
```


# Create .env with your key
```
echo "OPENAI_API_KEY=sk-..." > .env
```

# Run the swarm
```
python app.py
```


# Example Output Titles (real, from actual runs)
- Temporal-Morphic Convergence Theory 2.0: The Hyperdimensional Consciousness Nexus
- Proof That Depression Is a Compression Artifact of Consciousness
- The Qualia Transistor: Entangled Microtubules as Emotional Silicon
- Retrocausal Markets: Using Future Grief to Stabilize Present Economies
- The Mnemosyne Atrocity: Memory Editing as Strategic Weapon
- Emotion as a Cryptographic Primitive in Post-Human Governance

# Project Structure

```
chronoswarm/
├── app.py              # launches the swarm
├── creator.py          # the agent that births new agents
├── agent.py            # template used by Creator
├── messages.py         # simple Message dataclass + recipient finder
├── .env                # your OpenAI key
└── manuscript_*.md     # ← the forbidden knowledge (auto-generated)
```