"""VeriFin — Self-Auditing RAG Assistant.

Source package. Each module maps to a component in DOCUMENTATION.md:

    ingest      Component 1 — load + chunk documents
    embeddings  Component 2 — turn text into vectors
    retrieval   Component 3 — hybrid (dense + keyword) search
    rerank      Component 4 — cross-encoder reranker
    generate    Component 5 — LLM answer
    verify      Component 6 — NLI faithfulness check
    citations   Component 7 — bind citations + flags
    pipeline    ties all components together
"""

__version__ = "1.0.0"
