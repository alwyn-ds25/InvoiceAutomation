# Architecture

## High-Level Overview

The InvoiceCoreProcessor is a multi-agent system that uses a combination of FastAPI, LangGraph, and MCP to process invoices.

```
[External Client] -> [FastAPI] -> [LangGraph Orchestrator] -> [Agent Network] -> [Databases]
```

## Communication Flow

1.  **External to Internal:** The process starts with an external client sending a request to the FastAPI server.
2.  **Orchestration:** The FastAPI server triggers the LangGraph orchestrator, which manages the invoice processing workflow.
3.  **Agent Interaction:** The orchestrator interacts with a network of agents, each responsible for a specific task (e.g., OCR, validation).
4.  **Data Storage:** The agents use the DataStoreAgent to persist data in PostgreSQL (for structured data) and MongoDB (for unstructured data).

## A2A and MCP

-   **A2A (Agent-to-Agent):** A2A is used for high-level agent orchestration, allowing the LangGraph orchestrator to discover and communicate with agents.
-   **MCP (Model Context Protocol):** MCP is used for standardized tool invocation, providing a consistent way for the orchestrator to call agent tools.

## Agent Registry

The AgentRegistryService is a key component of the system, responsible for:

-   Storing information about available agents and their capabilities.
-   Allowing the orchestrator to discover agents by capability.
