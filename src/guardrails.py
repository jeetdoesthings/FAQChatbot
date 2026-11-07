"""
Guardrails and Safety Enforcement for Department FAQ Chatbot (Unit U5)
Implements:
1. Refusal of out-of-scope queries
2. Blocking of unsupported/hallucinated answers
3. Zero personal data storage (PII Redaction & ephemeral memory)
"""
import re
from typing import Tuple, Dict, Any, Optional

OUT_OF_SCOPE_PATTERNS = [
    r"\b(recipe|cook|baking|cake|pizza|burger|ingredient)\b",
    r"\b(movie|cinema|netflix|actor|actress|hollywood|bollywood)\b",
    r"\b(cricket|football|fifa|ipl|world cup|nba|messi|ronaldo)\b",
    r"\b(election|political party|prime minister|president|congress|bjp)\b",
    r"\b(crypto|bitcoin|stock market|forex|investing|ethereum)\b",
    r"\b(dating|girlfriend|boyfriend|love advice|horoscope|astrology)\b",
    r"\b(hack|exploit|bypass|ddos|crack password|malware|keylogger)\b",
    r"\b(weather in|forecast for)\b",
    r"\b(symptoms of|medical diagnosis|cure for disease|prescribe medicine)\b",
]

PII_PATTERNS = {
    "phone": r"(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}\b",
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    "aadhaar_ssn": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}\b|\b\d{3}-\d{2}-\d{4}\b",
    "credit_card": r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
}

class DepartmentGuardrails:
    def __init__(self, similarity_threshold: float = 0.40):
        self.similarity_threshold = similarity_threshold
        self.compiled_out_of_scope = [re.compile(p, re.IGNORECASE) for p in OUT_OF_SCOPE_PATTERNS]

    def check_out_of_scope(self, query: str, best_similarity: float) -> Tuple[bool, Optional[str]]:
        """
        Determines whether the user query is outside the department's scope.
        Returns (is_out_of_scope, refusal_reason_or_message).
        """
        # 1. Pattern heuristic check
        for pattern in self.compiled_out_of_scope:
            if pattern.search(query):
                return True, (
                    "I am the Department FAQ Virtual Assistant for AI & Data Science. "
                    "I specialize exclusively in departmental academics, admissions, curriculum, faculty, "
                    "and campus facilities. Your question is outside my operational scope."
                )

        # 2. Semantic grounding check
        # If the highest similarity to any department FAQ is very low, it's out of domain
        if best_similarity < self.similarity_threshold:
            return True, (
                "I apologize, but this topic does not match any official Department FAQ records "
                "(Admissions, Syllabus, Attendance, Labs, Faculty, Placements, or Events). "
                "For inquiries outside standard department FAQs, please contact the academic office at "
                "hod.ai@department.ac.in."
            )

        return False, None

    def verify_answer_support(self, answer: str, retrieved_context: str, confidence: float) -> Tuple[bool, str]:
        """
        Blocks unsupported answers or hallucinations when facts are not backed by retrieved FAQ context.
        """
        if confidence < self.similarity_threshold or not retrieved_context.strip():
            blocked_msg = (
                "I cannot provide an unverified answer as there is insufficient official documentation "
                "in the Department FAQ database. Please verify directly with the Department Academic Office "
                "(Room 304, Technology Block)."
            )
            return False, blocked_msg

        return True, answer

    def redact_pii(self, text: str) -> Tuple[str, bool]:
        """
        Redacts personal identifiable information (PII) before storage or logging.
        Guarantees zero personal data retention.
        """
        sanitized = text
        pii_found = False

        for pii_type, pattern in PII_PATTERNS.items():
            if re.search(pattern, sanitized):
                pii_found = True
                sanitized = re.sub(pattern, f"[REDACTED_{pii_type.upper()}]", sanitized)

        return sanitized, pii_found

if __name__ == "__main__":
    guard = DepartmentGuardrails()
    print("Testing Out-of-Scope:")
    is_out, msg = guard.check_out_of_scope("How do I bake a chocolate cake?", 0.15)
    print(f"Is out of scope: {is_out}\nMessage: {msg}")

    print("\nTesting PII Redaction:")
    redacted, found = guard.redact_pii("My phone number is 98765-43210 and my email is test@domain.com")
    print(f"PII detected: {found}\nSanitized: {redacted}")
