# System Architect Multi-Agent

A multi-agent RAG (Retrieval-Augmented Generation) system that analyzes and generates software architecture documentation. The system uses specialized AI agents to handle different aspects of system design including requirements analysis, use cases, security, API specifications, database design, and system architecture.

## Overview

The system employs an orchestrator pattern where multiple specialized agents work together to answer queries about software architecture and design. Each agent focuses on a specific domain and can collaborate with other agents to provide comprehensive answers.

### Agents

- **RequirementsAgent**: Extracts and analyzes functional and non-functional requirements
- **UseCaseAgent**: Analyzes use cases, actors, and flows
- **SecurityAgent**: Identifies security threats, vulnerabilities, and recommendations
- **APISpecAgent**: Provides API endpoint specifications and best practices
- **DBDesignerAgent**: Suggests database schemas and design patterns
- **SysArchitectAgent**: Recommends system architecture and component design

### Core Components

- **Orchestrator**: Intelligently routes queries to appropriate agents based on keywords and context
- **VectorStore**: Qdrant-based vector search using semantic embeddings for document retrieval
- **Cache**: Response caching system for improved performance
- **Context**: Manages conversation state and aggregates agent results

## Project Structure

```
System Architect/
├── .env                          # Environment variables (API keys)
├── .gitignore                    # Git ignore file
├── .venv/                        # Virtual environment
├── README.md                     # This file
│
├── app/
│   ├── __init__.py
│   │
│   ├── agents/                   # Agent implementations
│   │   ├── __init__.py
│   │   ├── apispec_agent.py      # API specification agent
│   │   ├── dbdesigner_agent.py   # Database design agent
│   │   ├── requirements_agent.py # Requirements analysis agent
│   │   ├── security_agent.py     # Security analysis agent
│   │   ├── sysarchitect_agent.py # System architecture agent
│   │   └── usecase_agent.py      # Use case analysis agent
│   │
│   ├── core/                     # Core components
│   │   ├── __init__.py
│   │   ├── base_agent.py         # Base agent class with LLM integration
│   │   ├── cache.py              # Response caching mechanism
│   │   ├── context.py            # Conversation context manager
│   │   ├── embeddings.py         # Text embedding functions
│   │   ├── orchestrator.py       # Agent orchestration logic
│   │   └── vector_store.py       # Vector search implementation
│   │
│   ├── data/                     # Raw documentation (local only, not in git)
│   │   ├── ApiSpecAgent/         # API documentation and examples
│   │   ├── DBDesignerAgent/      # Database design documents
│   │   ├── RequirementsAgent/    # Requirements specifications
│   │   ├── SecurityAgent/        # Security guidelines and best practices
│   │   ├── SysArchitectAgent/    # Architecture patterns and case studies
│   │   └── UseCaseAgent/         # Use case templates and examples
│   │
│   └── data_pipeline/            # Data processing pipeline
│       ├── __init__.py
│       ├── chunking.py           # Document chunking logic
│       └── documents.py          # Document loading utilities
│
└── main.py                       # Application entry point
```

## How It Works

1. **Document Ingestion**: Documents are loaded from the `app/data/` directories and split into chunks
2. **Embedding**: Each chunk is converted to a vector embedding using sentence transformers
3. **Indexing**: Embeddings are stored in an in-memory Qdrant vector database
4. **Query Processing**: User queries are routed to relevant agents by the orchestrator
5. **Retrieval**: Agents search the vector store using hybrid search (semantic + lexical)
6. **Generation**: Retrieved context is sent to OpenAI GPT-4 to generate responses
7. **Aggregation**: Results from multiple agents are combined into a final response

## Features

- **Hybrid Search**: Combines semantic (vector) and lexical (keyword) search for better retrieval
- **Multi-Agent Collaboration**: Agents can call other agents for comprehensive analysis
- **Response Caching**: MD5-based caching improves performance for repeated queries
- **Metadata Filtering**: Searches are filtered by document type for precision
- **Conversation Context**: Maintains state across multiple query turns
- **Source Attribution**: Tracks which documents contributed to each response
