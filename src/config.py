"""
Configuration settings for Department FAQ Voice Chatbot
"""
import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
OUTPUT_DIR = BASE_DIR / "outputs"
POSTERS_DIR = OUTPUT_DIR / "posters"
AUDIO_DIR = OUTPUT_DIR / "audio"

for directory in [DATA_DIR, MODELS_DIR, OUTPUT_DIR, POSTERS_DIR, AUDIO_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

FAQ_JSON_PATH = DATA_DIR / "department_faqs.json"
LORA_DATASET_PATH = DATA_DIR / "lora_faq_dataset.jsonl"
LORA_OUTPUT_DIR = MODELS_DIR / "faq_lora_adapter"

# Sentence-BERT Embedding Model
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
RAG_SIMILARITY_THRESHOLD = 0.35  # Queries below this similarity threshold are treated as out-of-domain or ungrounded
RAG_TOP_K = 3

# Base LLM Settings
BASE_MODEL_NAME = "distilgpt2" # Lightweight, CPU/MPS compatible base model for local LoRA fine-tuning and inference
MAX_HISTORY_TURNS = 5          # Sliding multi-turn conversation memory window

# Guardrail settings
ENABLE_GUARDRAILS = True
PII_REDACTION_ENABLED = True

# Department Identity
DEPARTMENT_TITLE = "Department of Artificial Intelligence & Data Science"
COLLEGE_TITLE = "Faculty of Technology & Engineering"
SUPPORT_EMAIL = "hod.ai@department.ac.in"
OFFICE_LOCATION = "Room 304, Third Floor, Technology Block"
