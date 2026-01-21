# Layered Memory for LLM Agents 🧠💻

This project implements a **Layered Memory architecture** for LLM-based agents, separating memory into **Semantic**, **Episodic**, and **Procedural** layers, coordinated through a central **Memory Manager** and executed via an **agent loop**.

The goal is to move beyond a stateless chatbot and build an agent that **remembers, reasons, uses tools, and decides when to stop**.

---

## 🚀 High-Level Architecture

### Core Concepts

#### Semantic Memory
- Stores **long-term factual knowledge**  
- Vector-based, backed by **Qdrant** or other vector databases  
- Supports retrieval of facts for reasoning and generation

#### Episodic Memory
- Maintains **session-scoped conversation history** and summaries  
- Enables context-aware interactions across turns

#### Procedural Memory
- Captures **learned behaviors, tool usage patterns, and workflows**  
- Guides agent actions and decision-making

#### Memory Manager
- Orchestrates reading and writing to memory layers  
- Decides what context to retrieve and store, when to update memory

#### LLM Loop
- Integrates all memory layers  
- Reasoning over retrieved memory  
- Invokes tools, performs actions, and decides whether to continue or stop

