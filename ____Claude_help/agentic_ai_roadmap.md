# 🚀 Agentic AI, MCP Server এবং RAG — সম্পূর্ণ Learning Roadmap

> **তোমার Background:** Python Basic + RHCE (RHEL 6.0, 2024)
> **লক্ষ্য:** Agentic AI, RAG, এবং MCP Server-এ Deep Knowledge অর্জন করা

---

## 📋 Roadmap Overview — কোনটার পর কোনটা শিখবে?

```
[Phase 0] Python Refresh + Linux Tools
      ↓
[Phase 1] LLM ও GenAI Fundamentals
      ↓
[Phase 2] RAG (Retrieval-Augmented Generation)
      ↓
[Phase 3] Agentic AI (LangChain → LangGraph → CrewAI)
      ↓
[Phase 4] MCP Server (Model Context Protocol)
      ↓
[Phase 5] Real-World Projects + Deployment
```

> **কেন এই Order?**
> RAG বুঝলে তবেই Agent-এর "memory" বুঝবে। Agent বুঝলে তবেই MCP-এর
> দরকারটা বুঝবে। এই sequence follow না করলে MCP পড়তে গিয়ে confused হবে।

---

## ⏱️ Estimated Timeline

| Phase | বিষয় | সময় |
|-------|-------|------|
| 0 | Python Refresh + Tools | ১–২ সপ্তাহ |
| 1 | LLM Fundamentals | ২ সপ্তাহ |
| 2 | RAG | ৩–৪ সপ্তাহ |
| 3 | Agentic AI | ৪–৫ সপ্তাহ |
| 4 | MCP Server | ২–৩ সপ্তাহ |
| 5 | Projects & Deploy | ৩–৪ সপ্তাহ |
| **মোট** | | **৩–৪ মাস** |

---

## 🔷 PHASE 0 — Python Refresh + Essential Tools (১–২ সপ্তাহ)

### কী কী দরকার?
AI engineering-এ যে Python features সবচেয়ে বেশি লাগে:
- `async/await` (asyncio)
- Decorators
- Type hints (Pydantic)
- Virtual Environment (venv / conda)
- API calls (requests, httpx)

### Resources

**YouTube:**
- 🎬 [Python Async IO — Tech With Tim (English)](https://www.youtube.com/watch?v=t3JUfblc2kc)
- 🎬 [Krish Naik — Python for GenAI (Hindi)](https://www.youtube.com/watch?v=7qqGnuRrWxg)

**Website / Documentation:**
- 📖 [Real Python — Async IO Guide](https://realpython.com/async-io-python/)
- 📖 [Pydantic Official Docs](https://docs.pydantic.dev/latest/)
- 📖 [Python Virtual Environments](https://docs.python.org/3/library/venv.html)

### Tools Install করো
```bash
# Python এবং pip আছে ধরে নিচ্ছি (Linux RHEL জানো তাই)
pip install langchain openai anthropic pydantic python-dotenv
pip install chromadb faiss-cpu sentence-transformers
pip install langgraph crewai fastmcp
```

---

## 🔷 PHASE 1 — LLM ও GenAI Fundamentals (২ সপ্তাহ)

### কী বুঝতে হবে?
- LLM (Large Language Model) কী?
- Token, Context Window, Temperature, Prompt Engineering
- OpenAI API / Anthropic Claude API ব্যবহার
- Embedding কী এবং কেন দরকার?
- Vector Database কী? (Chroma, FAISS, Pinecone)

### Resources

**YouTube:**
- 🎬 [Krish Naik — Complete LangChain Course (Hindi/English)](https://www.youtube.com/watch?v=7qqGnuRrWxg)
- 🎬 [freeCodeCamp — LangChain Crash Course (English)](https://www.youtube.com/watch?v=lG7Uxts9SXs)
- 🎬 [3Blue1Brown — Neural Networks Visualized (English)](https://www.youtube.com/watch?v=aircAruvnKk)

**Website / Blog:**
- 📖 [LangChain Official Documentation](https://docs.langchain.com)
- 📖 [OpenAI API Docs](https://platform.openai.com/docs)
- 📖 [What are Embeddings? — OpenAI Blog](https://openai.com/research/embedding)
- 📖 [The Illustrated Transformer — Jay Alammar](https://jalammar.github.io/illustrated-transformer/)

**Mini Project:**
একটা simple chatbot বানাও যেটা OpenAI / Groq API দিয়ে কথা বলে।

---

## 🔷 PHASE 2 — RAG (Retrieval-Augmented Generation) (৩–৪ সপ্তাহ)

### RAG কী?

RAG মানে হলো — LLM-এর নিজের জ্ঞানের বাইরে তোমার নিজের document/data থেকে
answer তৈরি করা। যেমন, তোমার company-র PDF থেকে AI-কে প্রশ্ন করতে পারবে।

```
তোমার PDF/Document
       ↓
   Chunks তৈরি
       ↓
   Embedding (সংখ্যায় রূপান্তর)
       ↓
   Vector Database-এ Store
       ↓
User Question → Similar Chunks খোঁজো → LLM-এ পাঠাও → Answer পাও
```

### RAG-এর ৩টি Stage শিখতে হবে
1. **Indexing** — Document load → Chunk → Embed → Store
2. **Retrieval** — User query → Similar chunks খোঁজা
3. **Generation** — Retrieved context + Query → LLM → Final Answer

### Resources

**YouTube (সবচেয়ে Important):**
- 🎬 [Learn RAG From Scratch — LangChain Engineer, freeCodeCamp (English)](https://www.youtube.com/watch?v=sVcwVQRHIc8)
  *(LangChain-এর নিজের engineer বানিয়েছেন — সেরা resource)*
- 🎬 [Complete RAG Crash Course — Krish Naik (Hindi/English, ২ ঘণ্টা)](https://www.youtube.com/watch?v=o126p1QN_RI)
- 🎬 [RAG with LangChain Full Tutorial (English)](https://www.youtube.com/watch?v=YLPNA1j7kmQ)
- 🎬 [Production RAG with LangChain & Vector Databases (English)](https://www.youtube.com/watch?v=mHxLXzYjQRE)

**Website / Blog:**
- 📖 [LangChain RAG Tutorial — Official](https://python.langchain.com/docs/tutorials/rag/)
- 📖 [RAG from Scratch — LangChain GitHub](https://github.com/langchain-ai/rag-from-scratch)
- 📖 [Advanced RAG Techniques — Towards Data Science](https://towardsdatascience.com/advanced-rag-techniques-an-illustrated-overview-04d193d8fec6)
- 📖 [DataCamp — RAG with LangChain Course](https://www.datacamp.com/courses/retrieval-augmented-generation-rag-with-langchain)

**Advanced RAG Topics (পরে):**
- HyDE (Hypothetical Document Embeddings)
- Self-Query Retrieval
- Multi-Vector Retrieval
- Reranking (Cohere Rerank)
- Agentic RAG

**Mini Projects:**
1. নিজের PDF থেকে Q&A chatbot
2. Wikipedia থেকে Real-time RAG
3. Multiple documents থেকে একসাথে search

---

## 🔷 PHASE 3 — Agentic AI (৪–৫ সপ্তাহ)

### Agentic AI কী?

সাধারণ chatbot শুধু উত্তর দেয়। কিন্তু **Agent** নিজে plan করে, tool ব্যবহার করে,
এবং steps নিজে decide করে।

```
User: "আমার এই research paper summary করো এবং email পাঠাও"

Agent:
  Step 1: PDF tool দিয়ে paper পড়লো
  Step 2: Summarization tool দিয়ে summary বানালো
  Step 3: Email tool দিয়ে send করলো
  ✅ Done!
```

### শেখার Order:

#### Week 1–2: LangChain Basics + Tools
- Chains, Prompts, Memory
- Tool calling / Function calling
- Simple ReAct Agent

#### Week 3–4: LangGraph
- State machines দিয়ে complex workflow
- Multi-step reasoning
- Human-in-the-loop

#### Week 5: CrewAI — Multi-Agent Systems
- Multiple agents একসাথে কাজ করে
- Role-based agents
- Agent collaboration

### Resources

**YouTube:**
- 🎬 [Agentic AI Full Course — LangGraph Zero to Hero Part 1 (English)](https://www.youtube.com/watch?v=4RtKGasvNC0)
- 🎬 [Agentic AI Full Course — LangGraph Zero to Hero Part 2 (English)](https://www.youtube.com/watch?v=YIv_GDxJqbA)
- 🎬 [LangGraph Complete Course for Beginners (English)](https://www.youtube.com/watch?v=jGg_1h0qzaM)
- 🎬 [Agentic AI Tutorial for Beginners — LangGraph (English)](https://www.youtube.com/watch?v=CnXdddeZ4tQ)
- 🎬 [CrewAI Tutorial — Beginners (English)](https://www.youtube.com/watch?v=G42J2MSKyc8)
- 🎬 [Complete Agentic AI Course 10 Hours — Krish Naik (Hindi/English)](https://www.youtube.com/watch?v=rV3HJ4LEZ7k)

**Website / Blog:**
- 📖 [LangGraph Official Documentation](https://langchain-ai.github.io/langgraph/)
- 📖 [LangChain Official Learn Page](https://docs.langchain.com/oss/python/learn)
- 📖 [CrewAI Official Documentation](https://docs.crewai.com)
- 📖 [IBM Coursera — Agentic AI with LangGraph & CrewAI (Free Audit)](https://www.coursera.org/learn/agentic-ai-with-langgraph-crewai-autogen-and-beeai)
- 📖 [Agentic AI Patterns — Neural Maze Blog](https://theneuralmaze.substack.com)
- 📖 [Agentic AI Design Patterns — PySquad](https://pysquad.com/blogs/agentic-ai-with-python-building-autonomous-agents-using-langgraph-and-crewai)

**Agent Frameworks তুলনা:**

| Framework | কখন ব্যবহার করবে |
|-----------|-----------------|
| LangChain | Basic chains, simple agents |
| LangGraph | Complex state-based workflows |
| CrewAI | Multi-agent collaboration |
| AutoGen | Conversational multi-agent |

---

## 🔷 PHASE 4 — MCP Server (Model Context Protocol) (২–৩ সপ্তাহ)

### MCP কী?

MCP হলো Anthropic-এর তৈরি একটা open protocol। এটা দিয়ে AI models
(Claude, GPT, ইত্যাদি) তোমার নিজের tools, database, এবং APIs-এর সাথে
**standardized** উপায়ে কথা বলতে পারে।

```
AI Model (Claude/GPT)
        ↕ MCP Protocol
   MCP Server (তোমার বানানো)
        ↕
তোমার Database / API / File System
```

**কেন MCP?**
আগে প্রতিটা AI-এর জন্য আলাদা integration লিখতে হতো। MCP দিয়ে
একটা server বানালেই সব AI connect করতে পারে।

### MCP-এর ৩টি Core Primitive:
1. **Tools** — AI যে functions call করতে পারে
2. **Resources** — File/data যা AI পড়তে পারে
3. **Prompts** — Pre-built prompt templates

### Resources

**YouTube:**
- 🎬 [Build MCP Server in 10 Minutes Python (English)](https://www.youtube.com/watch?v=AE04ehbAE78)

**Official Docs (সবচেয়ে Important):**
- 📖 [MCP Official Documentation — Anthropic](https://modelcontextprotocol.io/docs/develop/build-server)
- 📖 [MCP Python SDK — GitHub](https://github.com/modelcontextprotocol/python-sdk)
- 📖 [Anthropic MCP Course — Free](https://anthropic.skilljar.com/introduction-to-model-context-protocol)

**Blog / Tutorial:**
- 📖 [Build Your First MCP Server — Towards Data Science](https://towardsdatascience.com/model-context-protocol-mcp-tutorial-build-your-first-mcp-server-in-6-steps/)
- 📖 [Python MCP Server Guide — Real Python](https://realpython.com/python-mcp/)
- 📖 [How to Build MCP Server — freeCodeCamp](https://www.freecodecamp.org/news/how-to-build-your-own-mcp-server-with-python/)
- 📖 [MCP Server Production Guide — MCP Showcase](https://mcpshowcase.com/blog/create-mcp-server-with-python)

**MCP Server Example Code:**
```python
from fastmcp import FastMCP

mcp = FastMCP("আমার প্রথম MCP Server")

@mcp.tool()
def add(a: int, b: int) -> int:
    """দুটো সংখ্যা যোগ করে"""
    return a + b

@mcp.resource("config://settings")
def get_settings() -> str:
    """App settings পড়ে"""
    return "setting_value=123"

if __name__ == "__main__":
    mcp.run()
```

---

## 🔷 PHASE 5 — Real-World Projects + Deployment (৩–৪ সপ্তাহ)

### Capstone Projects (portfolio-ready)

#### Project 1: Personal Document Assistant (RAG)
- নিজের PDF, notes, documents upload করো
- যেকোনো প্রশ্ন করো — AI answer দেবে
- Stack: LangChain + ChromaDB + Streamlit

#### Project 2: Research Agent (Agentic AI)
- Topic দাও → Agent web search করে → Summary তৈরি করে → Email পাঠায়
- Stack: LangGraph + Tavily Search Tool + Gmail Tool

#### Project 3: Custom MCP Server
- নিজের database-এর জন্য MCP Server বানাও
- Claude Desktop থেকে সেটা ব্যবহার করো
- Stack: FastMCP + SQLite + Claude Desktop

#### Project 4: Multi-Agent System (Advanced)
- Writer Agent + Researcher Agent + Editor Agent — একসাথে কাজ করে
- Stack: CrewAI + LangGraph + RAG

### Deployment Resources
- 📖 [Deploy LangChain App — LangServe](https://python.langchain.com/docs/langserve/)
- 📖 [Docker + FastAPI Deploy Guide](https://fastapi.tiangolo.com/deployment/docker/)
- 📖 [Streamlit Cloud Deploy (Free)](https://streamlit.io/cloud)

---

## 📚 Best Books — Reference

### Tier 1 (সবচেয়ে গুরুত্বপূর্ণ)

| Book | Author | কী শিখবে |
|------|--------|----------|
| **Generative AI with LangChain (2nd Ed.)** | Ben Auffarth, Leonid Kuligin | LangChain, LangGraph, RAG, Multi-agent — সব একসাথে |
| **AI Engineering** | Chip Huyen | Production-level AI systems বানানো |

- 🔗 [Generative AI with LangChain — O'Reilly](https://www.oreilly.com/library/view/generative-ai-with/9781837022014)
- 🔗 [AI Engineering — Chip Huyen (Amazon)](https://www.amazon.com/AI-Engineering-Building-Applications-Foundation/dp/1098166302)

### Tier 2 (Advanced)

| Book | Author | কী শিখবে |
|------|--------|----------|
| **Build AI Agents with LangChain & LangGraph** | Jude Max | Practical agent building |
| **Hands-On LLMs** | Jay Alammar, Maarten Grootendorst | LLM internals + RAG + Agents |

- 🔗 [Build AI Agents — Amazon](https://www.amazon.com/Build-Agents-LangChain-LangGraph-Applications/dp/B0FDWQPSH2)
- 🔗 [Hands-On LLMs — Free Online](https://www.llm-course.com)

### Free Online Book
- 🔗 [The Illustrated Transformer — Jay Alammar](https://jalammar.github.io/illustrated-transformer/) *(LLM বোঝার সেরা ফ্রি resource)*

---

## 🛠️ Essential Tools & Stack

| Category | Tool | Link |
|----------|------|------|
| LLM Framework | LangChain / LangGraph | [docs.langchain.com](https://docs.langchain.com) |
| Vector DB (Local) | ChromaDB | [trychroma.com](https://www.trychroma.com) |
| Vector DB (Cloud) | Pinecone | [pinecone.io](https://www.pinecone.io) |
| LLM Provider | Groq (Free + Fast) | [console.groq.com](https://console.groq.com) |
| LLM Provider | OpenAI | [platform.openai.com](https://platform.openai.com) |
| Local LLM | Ollama | [ollama.ai](https://ollama.ai) |
| Multi-Agent | CrewAI | [docs.crewai.com](https://docs.crewai.com) |
| MCP Server | FastMCP | [github.com/jlowin/fastmcp](https://github.com/jlowin/fastmcp) |
| Monitoring | LangSmith | [smith.langchain.com](https://smith.langchain.com) |
| UI Deploy | Streamlit | [streamlit.io](https://streamlit.io) |
| Code Editor | VS Code + GitHub Copilot | [code.visualstudio.com](https://code.visualstudio.com) |

---

## 🎯 সেরা YouTube Channels (Subscribe করো)

| Channel | Language | Focus |
|---------|----------|-------|
| [Krish Naik](https://www.youtube.com/@krishnaik06) | Hindi + English | RAG, Agents, LangChain — beginner-friendly |
| [LangChain Official](https://www.youtube.com/@LangChain) | English | LangGraph, RAG — canonical patterns |
| [AssemblyAI](https://www.youtube.com/@AssemblyAI) | English | Practical AI engineering |
| [freeCodeCamp.org](https://www.youtube.com/@freecodecamp) | English | Long-form full courses |
| [The Neural Maze](https://www.youtube.com/@theNeuralMaze) | English | MCP, Agentic RAG, advanced topics |

---

## ⚡ Quick Start — আজই শুরু করো

১. **Groq-এ ফ্রি account খোলো:** [console.groq.com](https://console.groq.com)
   (OpenAI-এর চেয়ে অনেক fast, এবং ফ্রিতে API key দেয়)

২. **এই video দিয়ে শুরু করো:**
   [Krish Naik — Complete LangChain Course (Hindi)](https://www.youtube.com/watch?v=7qqGnuRrWxg)

৩. **প্রথম ছোট project:** একটা `.txt` file থেকে Q&A chatbot

৪. তারপর roadmap অনুযায়ী এগিয়ে যাও।

---

## 💡 গুরুত্বপূর্ণ পরামর্শ

> **"Tutorial Hell" থেকে বাঁচো।**
> প্রতিটা Phase শেষে একটা ছোট project বানাও।
> শুধু video দেখলে শেখা হয় না — code করলে শেখা হয়।

> **RHCE background তোমার কাজে আসবে।**
> Linux, networking, server management — এগুলো deployment-এ directly কাজে লাগবে।
> Docker, systemd, nginx — এসব তুমি এমনিতেই জানো।

---

*Roadmap তৈরি: July 2025 | Resources verified: 2025–2026*
