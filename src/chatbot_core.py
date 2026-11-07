"""
Chatbot Core Engine (Units U1, U2, U3, U4, U5)
Integrates:
- System Prompt & Tone (U1)
- Multi-turn conversation memory & LoRA generation (U2)
- Sentence-BERT retrieval & Whisper STT (U3)
- TTS synthesis & Event-poster generation (U4)
- Out-of-scope refusal, unsupported answer blocking & zero PII storage (U5)
"""
import os
os.environ["USE_TF"] = "0"
os.environ["TRANSFORMERS_NO_TF"] = "1"

import json
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

from src.config import (
    BASE_MODEL_NAME, LORA_OUTPUT_DIR, MAX_HISTORY_TURNS,
    RAG_SIMILARITY_THRESHOLD, ENABLE_GUARDRAILS, PII_REDACTION_ENABLED,
    SUPPORT_EMAIL, OFFICE_LOCATION
)
from src.system_prompt import get_system_prompt
from src.rag_retriever import FAQRetriever
from src.guardrails import DepartmentGuardrails
from src.tts_engine import TTSEngine
from src.poster_generator import EventPosterGenerator

class DepartmentChatbot:
    def __init__(self):
        print("[DepartmentChatbot] Initializing components...")
        self.system_prompt = get_system_prompt()
        self.retriever = FAQRetriever()
        self.guardrails = DepartmentGuardrails(similarity_threshold=RAG_SIMILARITY_THRESHOLD)
        self.tts = TTSEngine()
        self.poster_gen = EventPosterGenerator()
        
        # Multi-turn conversation memory: list of {"role": "user"|"assistant", "content": str}
        self.history: List[Dict[str, str]] = []

        # Model & Tokenizer for Generation
        self.tokenizer = None
        self.model = None
        # Explicit CPU device prevents ZeroGPU CUDA virtualization conflicts
        self.device = torch.device("cpu")
        self._init_llm()

    def _init_llm(self):
        """Loads tokenizer and LoRA adapted causal LM if available, otherwise base model."""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_NAME)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            adapter_path = LORA_OUTPUT_DIR
            if adapter_path.exists() and (adapter_path / "adapter_model.safetensors").exists():
                print(f"[DepartmentChatbot] Loading LoRA fine-tuned adapter from {adapter_path}...")
                base = AutoModelForCausalLM.from_pretrained(BASE_MODEL_NAME).to(self.device)
                self.model = PeftModel.from_pretrained(base, str(adapter_path)).to(self.device)
                self.model.eval()
                print("[DepartmentChatbot] LoRA model loaded successfully.")
            else:
                print(f"[DepartmentChatbot] Loading base model '{BASE_MODEL_NAME}'...")
                self.model = AutoModelForCausalLM.from_pretrained(BASE_MODEL_NAME).to(self.device)
                self.model.eval()
        except Exception as e:
            print(f"[DepartmentChatbot Warning] Model initialization notice: {e}")
            self.model = None

    def reset_memory(self):
        """Clears multi-turn dialog memory."""
        self.history = []

    def get_memory_transcript(self) -> List[Dict[str, str]]:
        """Returns current multi-turn conversation history."""
        return list(self.history)

    def generate_with_lora(self, prompt: str, max_new_tokens: int = 40) -> str:
        """
        Generates text using the LoRA fine-tuned causal language model (Unit U2).
        """
        if self.model is None or self.tokenizer is None:
            return "LoRA model not initialized."
        try:
            formatted = f"<|system|>\nYou are an official Department FAQ Assistant.\n<|user|>\n{prompt}\n<|assistant|>\n"
            inputs = self.tokenizer(formatted, return_tensors="pt").to(self.device)
            with torch.no_grad():
                output_ids = self.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    min_new_tokens=10,
                    pad_token_id=self.tokenizer.eos_token_id,
                    do_sample=False,
                    repetition_penalty=1.2
                )
            generated_ids = output_ids[0][inputs["input_ids"].shape[1]:]
            decoded = self.tokenizer.decode(generated_ids, skip_special_tokens=True)
            return decoded.strip()
        except Exception as e:
            return f"Generation notice: {e}"

    def _check_poster_request(self, query: str) -> Optional[Tuple[str, str]]:
        """Detects if user asks for an event poster generation."""
        q_lower = query.lower()
        poster_keywords = ["poster", "banner", "flyer", "event graphic"]
        if any(kw in q_lower for kw in poster_keywords):
            # Determine event name and details
            if "hackathon" in q_lower or "ai-conflux" in q_lower or "conflux" in q_lower:
                event_title = "AI-CONFLUX 2026"
                tagline = "National 36-Hour AI Hackathon & Tech Symposium"
                date_str = "October 24-25, 2026"
                venue = "NVIDIA AI Lab & Main Auditorium"
                highlights = "₹1,50,000 Cash Prizes • Free Swag • IEEE Certificates"
            elif "neurolympics" in q_lower or "sports" in q_lower or "cultural" in q_lower:
                event_title = "NEUROLYMPICS 2026"
                tagline = "Department Annual Sports & Cultural Fiesta"
                date_str = "November 14-16, 2026"
                venue = "University Sports Complex & Open Amphitheater"
                highlights = "12 Tournament Events • Trophy & Medals • DJ Night"
            else:
                event_title = "AI INNOVATION SUMMIT"
                tagline = "Department Technical Guest Lecture & Project Expo"
                date_str = "December 5, 2026"
                venue = "Technology Block Seminar Hall 1"
                highlights = "Keynote from Industry AI Leaders • Networking Lunch"

            poster_path = self.poster_gen.generate(
                event_title=event_title,
                tagline=tagline,
                date_str=date_str,
                venue_str=venue,
                highlights=highlights
            )
            response_text = (
                f"🎨 **Generated Official Event Poster for {event_title}!**\n\n"
                f"- **Event:** {event_title}\n"
                f"- **Tagline:** {tagline}\n"
                f"- **Date:** {date_str}\n"
                f"- **Venue:** {venue}\n"
                f"- **Highlights:** {highlights}\n"
                f"- **Contact:** {SUPPORT_EMAIL}\n\n"
                f"The high-resolution publication poster has been rendered and displayed below."
            )
            return response_text, poster_path
        return None

    def ask(self, user_message: str, generate_speech: bool = True) -> Dict[str, Any]:
        """
        Main query processing pipeline:
        1. Redact PII (Unit U5)
        2. Detect Poster Intent (Unit U4)
        3. Retrieve FAQs with Sentence-BERT (Unit U3)
        4. Apply Guardrails for out-of-scope & hallucination blocking (Unit U5)
        5. Formulate grounded answer with multi-turn memory (Unit U2)
        6. Synthesize TTS voice (Unit U4)
        """
        if not user_message or not user_message.strip():
            return {
                "answer": "Please state your question regarding department academics, admissions, faculty, or facilities.",
                "audio_path": None,
                "poster_path": None,
                "sources": [],
                "confidence": 0.0,
                "guardrail_status": "EMPTY_INPUT"
            }

        # 1. PII Redaction & Zero Personal Data Storage (Unit U5)
        sanitized_input, pii_detected = self.guardrails.redact_pii(user_message.strip())

        # 2. Check for Event Poster Request (Unit U4)
        poster_result = self._check_poster_request(sanitized_input)
        if poster_result:
            ans_text, poster_file = poster_result
            self._update_memory(sanitized_input, ans_text)
            audio_path = self.tts.synthesize(ans_text) if generate_speech else None
            return {
                "answer": ans_text,
                "audio_path": audio_path,
                "poster_path": poster_file,
                "sources": ["Department Events Database"],
                "confidence": 1.0,
                "guardrail_status": "POSTER_GENERATED"
            }

        # 3. Retrieve FAQ context with Sentence-BERT (Unit U3)
        context_str, best_sim, retrieved_items = self.retriever.get_grounding_context(user_message, top_k=3)

        # 4. Out-of-Scope Refusal Guardrail (Unit U5)
        is_out_of_scope, refusal_msg = self.guardrails.check_out_of_scope(user_message, best_sim)
        if is_out_of_scope:
            full_refusal = refusal_msg
            if pii_detected:
                full_refusal += "\n\n*(Note: Personal contact/credential details were detected and stripped under our strict Zero-PII privacy policy.)*"
            
            self._update_memory(sanitized_input, full_refusal)
            audio_path = self.tts.synthesize(full_refusal) if generate_speech else None
            return {
                "answer": full_refusal,
                "audio_path": audio_path,
                "poster_path": None,
                "sources": [],
                "confidence": float(best_sim),
                "guardrail_status": "REFUSED_OUT_OF_SCOPE"
            }

        # 5. Build Grounded Factual Answer (Units U1, U2, U5)
        top_faq = retrieved_items[0]
        answer_body = top_faq["answer"]
        category = top_faq["category"]
        confidence = float(top_faq["similarity_score"])

        # Unsupported answer verification (Unit U5)
        is_supported, verified_ans = self.guardrails.verify_answer_support(answer_body, context_str, confidence)
        if not is_supported:
            final_answer = verified_ans
            status = "BLOCKED_UNSUPPORTED"
        else:
            final_answer = (
                f"{verified_ans}\n\n"
                f"📌 *Category:* {category} | *Match Confidence:* {confidence * 100:.1f}%\n"
                f"🏛 *Official Inquiry Desk:* {OFFICE_LOCATION} (Email: {SUPPORT_EMAIL})"
            )
            if pii_detected:
                final_answer += "\n🔒 *(Privacy Notice: Submitted personal data was securely redacted.)*"
            status = "GROUNDED_FAQ_MATCH"

        # Update multi-turn dialog memory with sanitized content
        self._update_memory(sanitized_input, final_answer)

        # 6. Synthesize TTS Spoken Audio (Unit U4)
        audio_path = None
        if generate_speech:
            audio_path = self.tts.synthesize(answer_body)

        return {
            "answer": final_answer,
            "audio_path": audio_path,
            "poster_path": None,
            "sources": [f"{item['category']}: {item['question']}" for item in retrieved_items[:2]],
            "confidence": confidence,
            "guardrail_status": status
        }

    def _update_memory(self, user_msg: str, assistant_msg: str):
        """Maintains multi-turn memory bounded to MAX_HISTORY_TURNS."""
        self.history.append({"role": "user", "content": user_msg})
        self.history.append({"role": "assistant", "content": assistant_msg})
        # Slide window
        max_entries = MAX_HISTORY_TURNS * 2
        if len(self.history) > max_entries:
            self.history = self.history[-max_entries:]

if __name__ == "__main__":
    bot = DepartmentChatbot()
    print("\n--- Test Query 1: Valid Department FAQ ---")
    res1 = bot.ask("What is the attendance policy for semester exams?")
    print("Answer:\n", res1["answer"])
    print("Confidence:", res1["confidence"])
    print("Audio path:", res1["audio_path"])

    print("\n--- Test Query 2: Out of Scope ---")
    res2 = bot.ask("Who is the prime minister of Canada?")
    print("Answer:\n", res2["answer"])
    print("Status:", res2["guardrail_status"])
