"""Retrieval-Augmented Generation: corpus → chunk → embed → store → retrieve → LLM.

Kept deliberately separate from the recommendation engine. Retrieval is real and
keyless by default (TF-IDF cosine over the stored corpus); an embedding provider
(Gemini) can be swapped in for semantic vectors. The LLM only *synthesises* an
answer from retrieved context and cites its sources — it never invents the facts.
"""
