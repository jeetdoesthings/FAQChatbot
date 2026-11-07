"""
Gradio Web Application for Department FAQ Voice Chatbot (Project P24)
Author: Jeet Ghegade (Roll No: 24, Class: AIA 2, Enrolment: ADT23SOCB0484)
Features:
- Multi-turn LLM Chat with Memory (U2)
- Whisper Voice Input (STT) & Sentence-BERT Semantic Retrieval (U3)
- Text-to-Speech Spoken Audio Output & Event Poster Studio (U4)
- Out-of-scope Refusal, Hallucination Blocking & Zero-PII Guardrails (U5)
- Public shareable Live URL via Gradio Frp tunneling
"""
# ZeroGPU initialization: MUST be the first import before torch/transformers/gradio
try:
    import spaces
except Exception:
    class spaces:
        @staticmethod
        def GPU(func=None, duration=None):
            if func is None:
                return lambda f: f
            return func

import os
os.environ["USE_TF"] = "0"
os.environ["TRANSFORMERS_NO_TF"] = "1"

import sys
import argparse
from pathlib import Path

# Compatibility patch for huggingface_hub HfFolder in Gradio 4.x
try:
    import huggingface_hub
    if not hasattr(huggingface_hub, "HfFolder"):
        from huggingface_hub import constants, get_token
        class HfFolder:
            @classmethod
            def save_token(cls, token: str) -> None:
                path_token = Path(constants.HF_TOKEN_PATH)
                path_token.parent.mkdir(parents=True, exist_ok=True)
                path_token.write_text(token)
            @classmethod
            def get_token(cls):
                return get_token()
            @classmethod
            def delete_token(cls) -> None:
                try:
                    Path(constants.HF_TOKEN_PATH).unlink()
                except Exception:
                    pass
        huggingface_hub.HfFolder = HfFolder
except Exception:
    pass

# Compatibility patch for pydantic 2.10+ boolean schemas in Gradio 4.x OpenAPI generator
try:
    import gradio_client.utils
    orig_get_type = gradio_client.utils.get_type
    def safe_get_type(s):
        if not isinstance(s, dict):
            return "Any"
        return orig_get_type(s)
    gradio_client.utils.get_type = safe_get_type

    orig_json_schema = gradio_client.utils._json_schema_to_python_type
    def safe_json_schema(s, defs=None):
        if not isinstance(s, dict):
            return "Any"
        return orig_json_schema(s, defs)
    gradio_client.utils._json_schema_to_python_type = safe_json_schema
except Exception:
    pass

# Compatibility patch for Starlette 0.38+ TemplateResponse argument order in Gradio 4.x
try:
    import starlette.templating
    orig_TemplateResponse = starlette.templating.Jinja2Templates.TemplateResponse
    def safe_TemplateResponse(self, *args, **kwargs):
        if len(args) >= 2 and isinstance(args[0], str) and isinstance(args[1], dict):
            name = args[0]
            context = args[1]
            request = context.get("request")
            return orig_TemplateResponse(self, request=request, name=name, context=context)
        return orig_TemplateResponse(self, *args, **kwargs)
    starlette.templating.Jinja2Templates.TemplateResponse = safe_TemplateResponse
except Exception:
    pass

import gradio as gr

from src.chatbot_core import DepartmentChatbot
from src.stt_whisper import WhisperSTT
from src.poster_generator import EventPosterGenerator, THEMES
from src.config import OUTPUT_DIR, SUPPORT_EMAIL

# Initialize singleton engines
print("[App] Initializing Chatbot and Whisper STT...")
bot = DepartmentChatbot()
stt = WhisperSTT(model_size="base")
poster_studio = EventPosterGenerator()

CUSTOM_CSS = """
.gradio-container {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    max-width: 1200px !important;
    margin: auto;
}
.header-badge {
    background: linear-gradient(135deg, #1e3a8a, #3b82f6);
    color: white;
    padding: 16px 24px;
    border-radius: 12px;
    margin-bottom: 20px;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
}
.header-badge h1 {
    margin: 0;
    font-size: 26px;
    font-weight: 700;
    color: white !important;
}
.header-badge p {
    margin: 6px 0 0 0;
    font-size: 14px;
    opacity: 0.95;
    color: #e0f2fe !important;
}
.meta-card {
    background-color: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 12px;
}
"""

@spaces.GPU
def handle_text_chat(user_message, chat_history):
    """Processes typed text messages."""
    if not user_message or not user_message.strip():
        return "", chat_history, None, "Enter a valid question.", "N/A"

    response = bot.ask(user_message, generate_speech=True)
    
    bot_reply = response["answer"]
    audio_out = response["audio_path"]
    status_label = f"Status: {response['guardrail_status']} (Confidence: {response['confidence']*100:.1f}%)"
    sources_label = "Sources: " + (", ".join(response["sources"]) if response["sources"] else "None (Refused/Out-of-Scope)")

    chat_history.append((user_message, bot_reply))
    return "", chat_history, audio_out, status_label, sources_label

@spaces.GPU
def handle_voice_chat(audio_input, chat_history):
    """Transcribes audio using Whisper then processes question."""
    if audio_input is None:
        return "", chat_history, None, "No audio recorded.", "N/A"

    transcription = stt.transcribe(audio_input)
    if not transcription or not transcription.strip():
        return "", chat_history, None, "Could not decipher speech. Please speak clearly into the microphone.", "N/A"

    response = bot.ask(transcription, generate_speech=True)
    
    bot_reply = f"🎙️ *Voice Input:* \"{transcription}\"\n\n{response['answer']}"
    audio_out = response["audio_path"]
    status_label = f"Status: {response['guardrail_status']} (Confidence: {response['confidence']*100:.1f}%)"
    sources_label = "Sources: " + (", ".join(response["sources"]) if response["sources"] else "None (Refused/Out-of-Scope)")

    chat_history.append((f"🎤 [Spoken] {transcription}", response["answer"]))
    return transcription, chat_history, audio_out, status_label, sources_label

def handle_clear_chat():
    """Resets conversation memory and UI."""
    bot.reset_memory()
    return [], None, "Memory Cleared", "N/A"

@spaces.GPU
def handle_poster_generation(title, tagline, date, venue, highlights, theme):
    """Generates an event poster via the studio tab."""
    poster_path = poster_studio.generate(
        event_title=title,
        tagline=tagline,
        date_str=date,
        venue_str=venue,
        highlights=highlights,
        theme_name=theme
    )
    return poster_path

# Quick sample prompts
SAMPLE_QUESTIONS = [
    "What are the eligibility criteria and fees for B.Tech AI?",
    "What is the department attendance policy for semester exams?",
    "Who is the HOD and what are his student office hours?",
    "What GPU and laboratory computing facilities are available?",
    "What are the highest and average placement packages?",
    "Generate an event poster for the AI-Conflux Hackathon",
    "How do I bake a chocolate cake at home? (Testing out-of-scope refusal)",
    "My phone number is 9876543210. Can you save my contact details? (Testing PII guardrail)"
]

def load_sample(sample_idx):
    return SAMPLE_QUESTIONS[sample_idx]

with gr.Blocks(title="Department FAQ Voice Chatbot | P24", css=CUSTOM_CSS, theme=gr.themes.Soft()) as demo:
    with gr.Row():
        gr.HTML(
            """
            <div class="header-badge">
                <h1>🏛️ Department FAQ Voice Chatbot</h1>
                <p><strong>Candidate Details:</strong> Jeet Ghegade | Roll No: 24 | Class: AIA 2 | Enrolment: ADT23SOCB0484</p>
                <p><strong>Architecture:</strong> Whisper STT • Sentence-BERT RAG • LoRA Domain Adaptation • TTS Audio • Guardrails & Privacy</p>
            </div>
            """
        )

    with gr.Tabs():
        # TAB 1: Chatbot (Voice & Text)
        with gr.Tab("💬 Voice & Text FAQ Assistant"):
            with gr.Row():
                with gr.Column(scale=7):
                    chatbot_ui = gr.Chatbot(label="Conversation (Multi-Turn Memory)", height=450, bubble_full_width=False)
                    
                    with gr.Row():
                        txt_input = gr.Textbox(
                            show_label=False,
                            placeholder="Type your department question here or choose a quick sample below...",
                            scale=8
                        )
                        btn_send = gr.Button("Ask Text 💬", variant="primary", scale=2)

                    with gr.Row():
                        audio_mic = gr.Audio(sources=["microphone", "upload"], type="filepath", label="Voice Input (Whisper STT)", scale=8)
                        btn_voice = gr.Button("Transcribe & Ask 🎙️", variant="secondary", scale=2)

                    with gr.Accordion("💡 Quick Sample Questions", open=False):
                        for i, sample in enumerate(SAMPLE_QUESTIONS):
                            gr.Button(f"👉 {sample}").click(
                                fn=lambda s=sample: s,
                                outputs=txt_input
                            )

                    btn_clear = gr.Button("🔄 Clear Conversation Memory", variant="stop")

                with gr.Column(scale=3):
                    gr.Markdown("### 🔊 Spoken Response (TTS)")
                    audio_player = gr.Audio(label="Voice Audio Player", autoplay=True)

                    gr.Markdown("### 🛡️ Guardrail & Retrieval Telemetry")
                    status_box = gr.Textbox(label="Safety Guardrail Status", value="Awaiting query...", interactive=False)
                    sources_box = gr.Textbox(label="Sentence-BERT Grounding Sources", value="N/A", interactive=False)

                    gr.Markdown(
                        """
                        **Enforced Policies (Unit U5):**
                        - 🚫 Strict out-of-scope refusal
                        - 🛑 Zero unsupported hallucinations
                        - 🔒 Automatic PII redaction & ephemeral session
                        """
                    )

            # Event bindings
            btn_send.click(
                fn=handle_text_chat,
                inputs=[txt_input, chatbot_ui],
                outputs=[txt_input, chatbot_ui, audio_player, status_box, sources_box]
            )
            txt_input.submit(
                fn=handle_text_chat,
                inputs=[txt_input, chatbot_ui],
                outputs=[txt_input, chatbot_ui, audio_player, status_box, sources_box]
            )
            btn_voice.click(
                fn=handle_voice_chat,
                inputs=[audio_mic, chatbot_ui],
                outputs=[txt_input, chatbot_ui, audio_player, status_box, sources_box]
            )
            btn_clear.click(
                fn=handle_clear_chat,
                outputs=[chatbot_ui, audio_player, status_box, sources_box]
            )

        # TAB 2: Event Poster Studio
        with gr.Tab("🎨 Event Poster Studio (Unit U4)"):
            gr.Markdown("### High-Resolution Department Event Poster Generator")
            gr.Markdown("Create publication-ready posters for symposiums, hackathons, guest lectures, and cultural events.")
            
            with gr.Row():
                with gr.Column(scale=5):
                    poster_title = gr.Textbox(label="Event Title", value="AI-CONFLUX 2026")
                    poster_tagline = gr.Textbox(label="Event Tagline / Subtitle", value="National 36-Hour Hackathon & Technical Symposium")
                    poster_date = gr.Textbox(label="Date & Duration", value="October 24-25, 2026")
                    poster_venue = gr.Textbox(label="Venue", value="NVIDIA GPU Labs & Main Auditorium")
                    poster_highlights = gr.Textbox(label="Key Highlights / Perks", value="₹1,50,000 Prizes • Industry Mentors • Free Swag • IEEE Certificates")
                    poster_theme = gr.Dropdown(label="Visual Theme", choices=list(THEMES.keys()), value="Cyber Deep Blue")
                    btn_gen_poster = gr.Button("Generate Event Poster 🎨", variant="primary")

                with gr.Column(scale=5):
                    poster_image_display = gr.Image(label="Generated Poster Preview", type="filepath")

            btn_gen_poster.click(
                fn=handle_poster_generation,
                inputs=[poster_title, poster_tagline, poster_date, poster_venue, poster_highlights, poster_theme],
                outputs=poster_image_display
            )

        # TAB 3: Architecture & LoRA Tuning
        with gr.Tab("📊 System Architecture & Metrics"):
            gr.Markdown(
                f"""
                ### Project P24 System Architecture & Technical Specifications
                - **Student:** Jeet Ghegade (Roll No: 24, AIA 2, Enrolment: ADT23SOCB0484)
                - **Official Repository:** [github.com/jeetdoesthings/FAQChatbot](https://github.com/jeetdoesthings/FAQChatbot)
                
                #### Unit Implementation Breakdown:
                1. **U1 — System Prompt & Scope:** Explicit domain bounding, professional academic tone, strict hallucination refusal, and anti-PII retention policies.
                2. **U2 — LoRA Domain Adaptation & Memory:** Parameter-Efficient Fine-Tuning ($r=8, \\alpha=16$) on department FAQ knowledge base with multi-turn sliding window memory.
                3. **U3 — Sentence-BERT Retrieval & Whisper STT:** 384-dimensional dense semantic embedding search (`all-MiniLM-L6-v2`) with cosine similarity thresholding and OpenAI Whisper speech transcription.
                4. **U4 — Text-to-Speech & Poster Studio:** Dual-engine audio synthesis (gTTS + macOS offline) and automated high-res Pillow graphic poster designer.
                5. **U5 — Safety Guardrails & Privacy:** Semantic out-of-scope barrier, unsupported response blocker, and regex-based PII redaction engine.
                """
            )
            # Display training loss plot if available
            loss_plot_path = OUTPUT_DIR / "lora_training_loss.png"
            if loss_plot_path.exists():
                gr.Image(value=str(loss_plot_path), label="LoRA Training Loss Curve")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Department FAQ Voice Chatbot")
    parser.add_argument("--share", action="store_true", help="Launch with public live Gradio tunnel URL")
    parser.add_argument("--port", type=int, default=7860, help="Local port (default: 7860)")
    args = parser.parse_args()

    # In Hugging Face Spaces, call demo.launch() directly without hardcoded server_name
    if os.environ.get("SPACE_ID"):
        print("[App] Running inside Hugging Face Spaces cloud environment...")
        demo.launch()
    else:
        print(f"[App] Starting Gradio application on port {args.port} (share={args.share})...")
        demo.launch(server_name="0.0.0.0", server_port=args.port, share=args.share)
