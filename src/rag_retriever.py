"""
Sentence-BERT FAQ Retrieval Engine (Unit U3)
Indexes department FAQ knowledge base and performs semantic similarity retrieval.
Uses dense Sentence-BERT vectors combined with lexical keyword boosts.
"""
import os
os.environ["USE_TF"] = "0"
os.environ["TRANSFORMERS_NO_TF"] = "1"

import re
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer

from src.config import FAQ_JSON_PATH, EMBEDDING_MODEL_NAME, RAG_SIMILARITY_THRESHOLD, RAG_TOP_K

class FAQRetriever:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(FAQRetriever, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, faq_path: Path = FAQ_JSON_PATH, model_name: str = EMBEDDING_MODEL_NAME):
        if self._initialized:
            return

        self.faq_path = Path(faq_path)
        self.model_name = model_name
        print(f"[FAQRetriever] Loading Sentence-BERT model: '{self.model_name}' on CPU...")
        self.model = SentenceTransformer(self.model_name, device="cpu")
        
        self.faqs: List[Dict[str, Any]] = []
        self.question_embeddings: np.ndarray = np.array([])
        self.answer_embeddings: np.ndarray = np.array([])
        
        self._load_and_index()
        self._initialized = True

    def _load_and_index(self):
        """Loads FAQ entries and pre-computes dense Sentence-BERT embeddings."""
        if not self.faq_path.exists():
            raise FileNotFoundError(f"FAQ file not found at {self.faq_path}")

        with open(self.faq_path, "r", encoding="utf-8") as f:
            self.faqs = json.load(f)

        questions = [item["question"] for item in self.faqs]
        answers = [item["answer"] for item in self.faqs]

        print(f"[FAQRetriever] Encoding {len(self.faqs)} FAQ questions and answers...")
        self.question_embeddings = self.model.encode(questions, convert_to_numpy=True, normalize_embeddings=True)
        self.answer_embeddings = self.model.encode(answers, convert_to_numpy=True, normalize_embeddings=True)
        print(f"[FAQRetriever] Successfully indexed {len(self.faqs)} FAQ documents.")

    def retrieve(self, query: str, top_k: int = RAG_TOP_K) -> List[Dict[str, Any]]:
        """
        Retrieves top_k most semantically relevant FAQ entries for a query.
        Combines question and answer dense similarity with keyword matching.
        """
        if not query or not query.strip():
            return []

        clean_q = query.strip()
        query_words = set(re.findall(r"\w+", clean_q.lower()))

        # Dense embedding of query
        query_embedding = self.model.encode([clean_q], convert_to_numpy=True, normalize_embeddings=True)[0]

        # Cosine similarity against questions and answers
        q_scores = np.dot(self.question_embeddings, query_embedding)
        a_scores = np.dot(self.answer_embeddings, query_embedding)

        combined_scores = []
        for i, item in enumerate(self.faqs):
            dense_score = max(float(q_scores[i]), float(a_scores[i]) * 0.95)
            
            # Keyword overlap boost
            kw_set = set(k.lower() for k in item.get("keywords", []))
            overlap = len(query_words.intersection(kw_set))
            kw_boost = min(0.20, overlap * 0.08)

            final_score = min(1.0, dense_score + kw_boost)
            combined_scores.append(final_score)

        combined_scores = np.array(combined_scores)
        top_indices = np.argsort(combined_scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            score = float(combined_scores[idx])
            faq_entry = dict(self.faqs[idx])
            faq_entry["similarity_score"] = round(score, 4)
            results.append(faq_entry)

        return results

    def get_grounding_context(self, query: str, top_k: int = RAG_TOP_K) -> Tuple[str, float, List[Dict[str, Any]]]:
        """
        Returns:
            context_str: Formatted context block for LLM prompt injection
            max_score: Highest similarity score among retrieved items
            results: List of retrieved entries
        """
        results = self.retrieve(query, top_k=top_k)
        if not results:
            return "", 0.0, []

        max_score = results[0]["similarity_score"]
        
        context_lines = ["--- VERIFIED DEPARTMENT FAQ KNOWLEDGE BASE ---"]
        for i, item in enumerate(results, 1):
            context_lines.append(
                f"[Doc {i}] Category: {item['category']}\n"
                f"Question: {item['question']}\n"
                f"Answer: {item['answer']}\n"
                f"Relevance Score: {item['similarity_score']}\n"
            )
        context_lines.append("-------------------------------------------------")
        return "\n".join(context_lines), max_score, results

if __name__ == "__main__":
    retriever = FAQRetriever()
    test_q = "How much attendance do I need for writing end sem exams?"
    context, best_score, items = retriever.get_grounding_context(test_q)
    print(f"\nQuery: {test_q}")
    print(f"Top Score: {best_score}")
    print(f"Top Matched Question: {items[0]['question']}")
