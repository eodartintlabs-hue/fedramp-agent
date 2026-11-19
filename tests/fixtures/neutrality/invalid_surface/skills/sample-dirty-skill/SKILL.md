---
name: sample-dirty-skill
description: Skill with forbidden vendor references and illegal frontmatter keys.
model: claude-3-7-sonnet
allowed-tools: Bash
---

# Sample Non-Compliant Skill

This file illegally names OpenAI, Anthropic, Gemini, ChatGPT, GPT-4, Cursor, Copilot, Windsurf, Antigravity, LangChain, CrewAI, AutoGen, Bedrock, and Vertex AI.
It also references `.claude/settings.json` and `.cursor/rules` and `<invoke the Bash tool>` and `subagent_type` and auto-triggers on load.
