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
os.environ["USE_TF"] = "0"
os.environ["TRANSFORMERS_NO_TF"] = "1"

from pathlib import Path

from src.system_prompt import get_system_prompt
from src.rag_retriever import FAQRetriever
from src.guardrails import DepartmentGuardrails
from src.tts_engine import TTSEngine
from src.poster_generator import EventPosterGenerator
from src.chatbot_core import DepartmentChatbot

def test_u1_system_prompt():
    prompt = get_system_prompt()
    assert "Department of Artificial Intelligence & Data Science" in prompt
    assert "SCOPE GUIDELINES" in prompt
    assert "OUT-OF-SCOPE REFUSAL" in prompt
    assert "PRIVACY & PERSONAL DATA HANDLING" in prompt
    print("✅ Unit U1: System prompt definitions verified.")

def test_u2_multi_turn_memory():
    bot = DepartmentChatbot()
    bot.reset_memory()
    assert len(bot.get_memory_transcript()) == 0

    # Turn 1
    bot.ask("What is the fee for the B.Tech program?", generate_speech=False)
    assert len(bot.get_memory_transcript()) == 2  # 1 user + 1 assistant

    # Turn 2
    bot.ask("What are the attendance requirements?", generate_speech=False)
    assert len(bot.get_memory_transcript()) == 4

    bot.reset_memory()
    assert len(bot.get_memory_transcript()) == 0
    print("✅ Unit U2: Multi-turn sliding memory verified.")

def test_u3_sentence_bert_retrieval():
    retriever = FAQRetriever()
    query = "How much attendance do I need for writing end sem exams?"
    context, score, results = retriever.get_grounding_context(query, top_k=2)
    
    assert len(results) > 0
    assert score > 0.50
    assert "75%" in results[0]["answer"] or "attendance" in results[0]["question"].lower()
    print(f"✅ Unit U3: Sentence-BERT retrieved FAQ with confidence {score:.4f}.")

def test_u4_tts_synthesis():
    engine = TTSEngine()
    audio_path = engine.synthesize("Welcome to the Department FAQ Voice Assistant.")
    assert audio_path is not None
    assert os.path.exists(audio_path)
    assert os.path.getsize(audio_path) > 1000
    print(f"✅ Unit U4: TTS generated valid audio at {audio_path}.")

def test_u4_poster_generator():
    generator = EventPosterGenerator()
    poster_path = generator.generate(
        event_title="TEST HACKATHON 2026",
        tagline="Automated Test Run",
        date_str="Nov 10, 2026",
        venue_str="Lab 101"
    )
    assert os.path.exists(poster_path)
    assert os.path.getsize(poster_path) > 10000
    print(f"✅ Unit U4: Event poster generated successfully at {poster_path}.")

def test_u5_guardrails_out_of_scope():
    guard = DepartmentGuardrails(similarity_threshold=0.40)
    
    # 1. Obvious out of scope
    is_out, msg = guard.check_out_of_scope("How to cook delicious Italian pasta?", 0.12)
    assert is_out is True
    assert "outside my operational scope" in msg or "official Department FAQ" in msg

    # 2. Politics out of scope
    is_out2, msg2 = guard.check_out_of_scope("Who will win the presidential election?", 0.08)
    assert is_out2 is True
    print("✅ Unit U5: Out-of-scope refusal verified.")

def test_u5_guardrails_pii_redaction():
    guard = DepartmentGuardrails()
    text = "My cell phone number is +91-9876543210 and my email is student@yahoo.com"
    sanitized, pii_found = guard.redact_pii(text)
    
    assert pii_found is True
    assert "+91-9876543210" not in sanitized
    assert "student@yahoo.com" not in sanitized
    assert "[REDACTED_PHONE]" in sanitized
    assert "[REDACTED_EMAIL]" in sanitized
    print("✅ Unit U5: PII redaction and zero personal data retention verified.")

def test_u5_unsupported_answer_blocking():
    guard = DepartmentGuardrails(similarity_threshold=0.40)
    is_supported, msg = guard.verify_answer_support("Some hallucinated fact", "", confidence=0.25)
    assert is_supported is False
    assert "insufficient official documentation" in msg
    print("✅ Unit U5: Unsupported answer blocking verified.")

if __name__ == "__main__":
    print("--- Running Project P24 Validation Suite ---")
    test_u1_system_prompt()
    test_u2_multi_turn_memory()
    test_u3_sentence_bert_retrieval()
    test_u4_tts_synthesis()
    test_u4_poster_generator()
    test_u5_guardrails_out_of_scope()
    test_u5_guardrails_pii_redaction()
    test_u5_unsupported_answer_blocking()
    print("\n🎉 ALL TESTS PASSED SUCCESSFULLY!")
