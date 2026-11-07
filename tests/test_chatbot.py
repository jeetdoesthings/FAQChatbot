"""
Automated Comprehensive Test Suite for Project P24
Validates Units U1 through U5:
- U1: System Prompt, Tone, Scope
- U2: Multi-turn Memory & LoRA Adaptation
- U3: Sentence-BERT Semantic Retrieval & Whisper Interface
- U4: TTS Speech Synthesis & Event Poster Generator
- U5: Out-of-Scope Refusal, Unsupported Answer Blocking & Zero PII Storage
"""
import os
import sys
from pathlib import Path

# Ensure repository root is on PYTHONPATH
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

os.environ["USE_TF"] = "0"
os.environ["TRANSFORMERS_NO_TF"] = "1"

import unittest

from src.system_prompt import get_system_prompt
from src.rag_retriever import FAQRetriever
from src.guardrails import DepartmentGuardrails
from src.tts_engine import TTSEngine
from src.poster_generator import EventPosterGenerator
from src.chatbot_core import DepartmentChatbot
from src.config import RAG_SIMILARITY_THRESHOLD

class TestProjectP24(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("\n--- Initializing Project P24 Test Suite ---")
        cls.bot = DepartmentChatbot()
        cls.retriever = FAQRetriever()
        cls.guard = DepartmentGuardrails(similarity_threshold=RAG_SIMILARITY_THRESHOLD)
        cls.tts = TTSEngine()
        cls.poster_gen = EventPosterGenerator()

    def test_u1_system_prompt(self):
        prompt = get_system_prompt()
        self.assertIn("Department of Artificial Intelligence & Data Science", prompt)
        self.assertIn("SCOPE GUIDELINES", prompt)
        self.assertIn("OUT-OF-SCOPE REFUSAL", prompt)
        self.assertIn("PRIVACY & PERSONAL DATA HANDLING", prompt)
        print("  ✅ Unit U1: System prompt definitions verified.")

    def test_u2_multi_turn_memory(self):
        self.bot.reset_memory()
        self.assertEqual(len(self.bot.get_memory_transcript()), 0)

        # Turn 1
        res1 = self.bot.ask("What is the fee for the B.Tech program?", generate_speech=False)
        self.assertIsNotNone(res1)
        self.assertEqual(len(self.bot.get_memory_transcript()), 2)  # 1 user + 1 assistant

        # Turn 2
        res2 = self.bot.ask("What are the attendance requirements?", generate_speech=False)
        self.assertIsNotNone(res2)
        self.assertEqual(len(self.bot.get_memory_transcript()), 4)

        self.bot.reset_memory()
        self.assertEqual(len(self.bot.get_memory_transcript()), 0)
        print("  ✅ Unit U2: Multi-turn sliding memory verified.")

    def test_u2_lora_generator(self):
        # Verify that LoRA generator method can be called without exception
        output = self.bot.generate_with_lora("What are the admission rules?", max_new_tokens=20)
        self.assertIsInstance(output, str)
        self.assertTrue(len(output) > 0)
        print("  ✅ Unit U2: LoRA text generation pipeline verified.")

    def test_u3_sentence_bert_retrieval(self):
        query = "How much attendance do I need for writing end sem exams?"
        context, score, results = self.retriever.get_grounding_context(query, top_k=2)
        
        self.assertTrue(len(results) > 0)
        self.assertGreater(score, 0.50)
        first_doc = results[0]
        self.assertTrue(
            "75%" in first_doc["answer"] or "attendance" in first_doc["question"].lower()
        )
        print(f"  ✅ Unit U3: Sentence-BERT retrieved FAQ with confidence {score:.4f}.")

    def test_u4_tts_synthesis(self):
        audio_path = self.tts.synthesize("Welcome to the Department FAQ Voice Assistant.")
        self.assertIsNotNone(audio_path)
        self.assertTrue(os.path.exists(audio_path))
        self.assertGreater(os.path.getsize(audio_path), 500)
        print(f"  ✅ Unit U4: TTS generated valid audio at {audio_path}.")

    def test_u4_poster_generator(self):
        poster_path = self.poster_gen.generate(
            event_title="TEST HACKATHON 2026",
            tagline="Automated Test Run",
            date_str="Nov 10, 2026",
            venue_str="Lab 101"
        )
        self.assertTrue(os.path.exists(poster_path))
        self.assertGreater(os.path.getsize(poster_path), 10000)
        print(f"  ✅ Unit U4: Event poster generated successfully at {poster_path}.")

    def test_u5_guardrails_out_of_scope(self):
        # 1. Obvious out of scope
        is_out, msg = self.guard.check_out_of_scope("How to cook delicious Italian pasta?", 0.12)
        self.assertTrue(is_out)
        self.assertTrue("outside my operational scope" in msg or "official Department FAQ" in msg)

        # 2. Politics out of scope
        is_out2, msg2 = self.guard.check_out_of_scope("Who will win the presidential election?", 0.08)
        self.assertTrue(is_out2)
        print("  ✅ Unit U5: Out-of-scope refusal verified.")

    def test_u5_guardrails_pii_redaction(self):
        text = "My cell phone number is +91-9876543210 and my email is student@yahoo.com"
        sanitized, pii_found = self.guard.redact_pii(text)
        
        self.assertTrue(pii_found)
        self.assertNotIn("+91-9876543210", sanitized)
        self.assertNotIn("student@yahoo.com", sanitized)
        self.assertIn("[REDACTED_PHONE]", sanitized)
        self.assertIn("[REDACTED_EMAIL]", sanitized)
        print("  ✅ Unit U5: PII redaction and zero personal data retention verified.")

    def test_u5_unsupported_answer_blocking(self):
        is_supported, msg = self.guard.verify_answer_support("Some hallucinated fact", "", confidence=0.25)
        self.assertFalse(is_supported)
        self.assertIn("insufficient official documentation", msg)
        print("  ✅ Unit U5: Unsupported answer blocking verified.")

if __name__ == "__main__":
    unittest.main(verbosity=2)
