"""
Academic PDF Report Generator for Project P24
Outputs: 24_Jeet_P24.pdf
Candidate: Jeet Ghegade | Roll No: 24 | Class: AIA 2 | Enrolment: ADT23SOCB0484
"""
import os
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        
        # Header (Pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, letter[1] - 36, "P24 · Department FAQ Voice Chatbot | GENAI Project Report")
            self.drawRightString(letter[0] - 54, letter[1] - 36, "Jeet Ghegade · Roll No: 24 · AIA 2")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(54, letter[1] - 42, letter[0] - 54, letter[1] - 42)

        # Footer (All pages)
        footer_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 54, 34, footer_text)
        self.drawString(54, 34, "Department of AI & Data Science · Enrolment: ADT23SOCB0484")
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 46, letter[0] - 54, 46)
        self.restoreState()

def build_pdf_report(output_filename="24_Jeet_P24.pdf"):
    pdf_path = Path(__file__).resolve().parent / output_filename
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        leftMargin=50,
        rightMargin=50,
        topMargin=50,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom color palette
    c_primary = colors.HexColor("#1e3a8a")     # Deep Navy
    c_secondary = colors.HexColor("#0284c7")   # Sky Blue
    c_dark = colors.HexColor("#0f172a")        # Slate 900
    c_gray = colors.HexColor("#475569")        # Slate 600
    c_bg_light = colors.HexColor("#f8fafc")    # Slate 50
    c_accent = colors.HexColor("#059669")      # Emerald

    # Typography styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=28,
        textColor=c_primary,
        alignment=1, # Center
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=12,
        leading=16,
        textColor=c_secondary,
        alignment=1,
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=c_primary,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        "Heading2_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=c_secondary,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=c_dark,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        "Bullet_Custom",
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=3
    )

    code_style = ParagraphStyle(
        "Code_Custom",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#1e293b"),
        backColor=colors.HexColor("#f1f5f9"),
        borderPadding=5,
        spaceAfter=6
    )

    callout_style = ParagraphStyle(
        "Callout",
        parent=body_style,
        fontSize=8.5,
        leading=12,
        textColor=c_primary,
        backColor=colors.HexColor("#eff6ff"),
        borderPadding=6,
        spaceAfter=8
    )

    story = []

    # Title & Header Banner
    story.append(Paragraph("GENAI PROJECT TECHNICAL REPORT", subtitle_style))
    story.append(Paragraph("P24 · Department FAQ Voice Chatbot", title_style))
    story.append(Paragraph("Multi-Turn Multimodal Agent with Whisper STT, Sentence-BERT RAG, LoRA Adaptation & Privacy Guardrails", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_primary, spaceBefore=4, spaceAfter=12))

    # Candidate Credentials Table
    cand_data = [
        [
            Paragraph("<b>Candidate Name:</b> Jeet Ghegade", body_style),
            Paragraph("<b>Roll Number:</b> 24", body_style)
        ],
        [
            Paragraph("<b>Class:</b> AIA 2", body_style),
            Paragraph("<b>Enrolment No:</b> ADT23SOCB0484", body_style)
        ],
        [
            Paragraph("<b>GitHub Repository:</b> <a href='https://github.com/jeetdoesthings/FAQChatbot'><font color='#0284c7'><b>github.com/jeetdoesthings/FAQChatbot</b></font></a>", body_style),
            Paragraph("<b>Live App Universal URL:</b> <a href='https://huggingface.co/spaces/gladiatorspring/FAQChatbot'><font color='#059669'><b>huggingface.co/spaces/gladiatorspring/FAQChatbot</b></font></a>", body_style)
        ],
        [
            Paragraph("<b>Project Domain:</b> Generative AI & Conversational Agents", body_style),
            Paragraph("<b>Evaluation Term:</b> Academic Year 2026", body_style)
        ]
    ]
    cand_table = Table(cand_data, colWidths=[3.2 * inch, 3.8 * inch])
    cand_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_bg_light),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(cand_table)
    story.append(Spacer(1, 10))

    # 1. Executive Summary & Project Goal
    story.append(Paragraph("1. Executive Summary & Project Objective", h1_style))
    summary_text = (
        "The <b>Department FAQ Voice Chatbot (Project P24)</b> is an intelligent conversational agent engineered to resolve "
        "academic, admission, curriculum, faculty, and administrative inquiries for university departments. "
        "The system seamlessly combines multimodal voice and text inputs across multi-turn conversational interactions with memory, "
        "grounded in verified departmental records to eliminate hallucinations. "
        "It achieves domain specialization via Parameter-Efficient Fine-Tuning (PEFT/LoRA) on an academic FAQ corpus, "
        "utilizes Sentence-BERT dense semantic retrieval, accepts spoken voice input through OpenAI Whisper, generates spoken "
        "responses using Text-to-Speech (TTS), dynamically renders publication-ready event posters, and enforces rigorous "
        "safety guardrails to reject out-of-scope prompts and guarantee zero personal data retention."
    )
    story.append(Paragraph(summary_text, body_style))

    # Architecture Overview Table
    arch_data = [
        ["Milestone Unit", "Technology Stack", "Core Functionality & Guarantee"],
        ["U1: System Prompt & Tone", "Prompt Engineering & Guardrails", "Enforces authoritative academic persona, explicit domain bounding, and respectful refusal."],
        ["U2: LLM Chat with Memory & LoRA", "DistilGPT2 + PEFT LoRA (r=8, a=16)", "Sliding window memory (5 turns); fine-tuned adapter reduces loss from 9.81 to 6.17."],
        ["U3: RAG Retrieval & Whisper STT", "Sentence-BERT + OpenAI Whisper", "384-d dense embeddings (all-MiniLM-L6-v2) with hybrid scoring + 16kHz speech-to-text."],
        ["U4: TTS & Event Poster Studio", "gTTS + Pillow Graphic Engine", "Dual-engine audio voice synthesis and automated 1080x1440 publication event poster renderer."],
        ["U5: Safety Guardrails & Privacy", "Regex Heuristics & Cosine Gates", "Refuses non-department queries, blocks ungrounded claims, and strips all PII on the fly."]
    ]
    arch_table = Table(arch_data, colWidths=[1.8 * inch, 2.2 * inch, 3.0 * inch])
    arch_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 8.5),
        ('BOTTOMPADDING', (0,0), (-1,0), 4),
        ('BACKGROUND', (0,1), (-1,-1), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(arch_table)
    story.append(Spacer(1, 10))

    # 2. Unit U1 — System Prompt & Scope
    story.append(Paragraph("2. Unit U1 — System Prompt, Scope & Tone", h1_style))
    story.append(Paragraph(
        "The system prompt establishes the foundational identity, operating boundaries, and tone of the virtual assistant. "
        "It mandates that all responses must be strictly grounded in official department facts, adopt a professional academic tone, "
        "and immediately disallow non-department inquiries.",
        body_style
    ))
    prompt_extract = (
        "<b>System Persona Directive:</b><br/>"
        "<i>\"You are the official Virtual Assistant for the Department of Artificial Intelligence & Data Science at the Faculty of "
        "Technology & Engineering. Your primary mission is to provide accurate, authoritative, and polite information regarding departmental "
        "academics, admissions, faculty office hours, research facilities, examinations, placements, and campus events... "
        "You MUST politely refuse questions outside departmental affairs. You do NOT collect, record, or retain any Personal Identifiable Information (PII).\"</i>"
    )
    story.append(Paragraph(prompt_extract, callout_style))

    # 3. Unit U2 — LLM Chat with Memory & LoRA Domain Adaptation
    story.append(Paragraph("3. Unit U2 — Conversational Memory & LoRA Fine-Tuning", h1_style))
    story.append(Paragraph(
        "<b>Multi-Turn Memory Architecture:</b> The chatbot maintains conversational context using a sliding window buffer bounded to "
        "<code>MAX_HISTORY_TURNS = 5</code>. Every turn pair (user query, assistant answer) is dynamically sanitized to strip PII before "
        "being appended into session state, ensuring context is preserved across turns without memory bloat or credential leakages.",
        body_style
    ))
    story.append(Paragraph(
        "<b>LoRA (Low-Rank Adaptation) Mathematical Formulation:</b> Rather than fine-tuning all 82M parameters of the base causal language model, "
        "LoRA decomposes parameter weight updates into two low-rank matrices <i>B</i> and <i>A</i>: "
        "<br/>&nbsp;&nbsp;&nbsp;&nbsp;<b>W = W<sub>0</sub> + &Delta;W = W<sub>0</sub> + (B &times; A) &times; (&alpha; / r)</b><br/>"
        "where <i>W<sub>0</sub> &isin; &Ropf;<sup>d &times; k</sup></i> represents the frozen pre-trained base model weights, "
        "<i>B &isin; &Ropf;<sup>d &times; r</sup></i>, <i>A &isin; &Ropf;<sup>r &times; k</sup></i> with rank <i>r = 8</i> and scaling factor &alpha; = 16. "
        "This drastically reduces trainable parameters to only <b>147,456 (0.18%)</b>, enabling rapid, energy-efficient domain adaptation.",
        body_style
    ))

    # LoRA Metrics Table
    lora_metrics_data = [
        ["Hyperparameter / Metric", "Value", "Technical Impact"],
        ["Base Model Architecture", "DistilGPT2 (Causal LM)", "Lightweight, low-latency autoregressive transformer (82M params)"],
        ["LoRA Rank (r) & Alpha (a)", "r = 8, a = 16 (Scaling = 2.0)", "Low intrinsic rank captures department FAQ structure with minimal drift"],
        ["Target Adapter Modules", "c_attn (Query/Key/Value Attention)", "Focuses parameter updates on self-attention projection layers"],
        ["Trainable Parameters", "147,456 / 82,060,032 (0.18%)", "99.82% parameters frozen, preventing catastrophic forgetting"],
        ["Training Loss (Pre -> Post)", "9.8137 &rarr; 6.1742", "Substantial cross-entropy reduction across 4 training epochs"],
        ["Perplexity (Pre -> Post)", "18,281.78 &rarr; 480.19", "Perplexity reduced by 97.4%, aligning syntax with academic inquiries"],
        ["Training Hardware / Device", "Apple Silicon MPS (Metal)", "Fully hardware-accelerated local tensor computation in 7.2 seconds"]
    ]
    lora_table = Table(lora_metrics_data, colWidths=[2.2 * inch, 2.0 * inch, 2.8 * inch])
    lora_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 8),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#f8fafc")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('FONTSIZE', (0,1), (-1,-1), 7.5),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(lora_table)
    story.append(Spacer(1, 8))

    # Embedding LoRA Loss Plot
    loss_img_path = Path(__file__).resolve().parent / "outputs" / "lora_training_loss.png"
    if loss_img_path.exists():
        story.append(KeepTogether([
            Paragraph("<b>Figure 1: LoRA Fine-Tuning Loss Convergence Curve</b>", h2_style),
            Image(str(loss_img_path), width=6.2 * inch, height=2.2 * inch),
            Spacer(1, 8)
        ]))

    # Page Break for clean layout
    story.append(PageBreak())

    # 4. Unit U3 — Sentence-BERT Semantic Retrieval & Whisper STT
    story.append(Paragraph("4. Unit U3 — Semantic Retrieval & Whisper Voice Input", h1_style))
    story.append(Paragraph(
        "<b>Dense Semantic Retrieval with Sentence-BERT:</b> Unlike fragile keyword search, the system encodes the department FAQ "
        "database using <code>all-MiniLM-L6-v2</code> into 384-dimensional dense vectors. During query inference, the user prompt is "
        "projected into the same latent space to compute cosine similarities against both question and answer representations: "
        "<br/>&nbsp;&nbsp;&nbsp;&nbsp;<b>Sim(q, d) = (u &middot; v) / (||u|| ||v||)</b><br/>"
        "A hybrid lexical boost adds up to +0.20 for exact keyword overlaps (e.g., 'fees', 'attendance', 'hod', 'gpu'). "
        "Queries falling below the threshold (&theta; = 0.35) are flagged as out-of-domain or ungrounded.",
        body_style
    ))
    story.append(Paragraph(
        "<b>OpenAI Whisper Speech-to-Text Pipeline:</b> Spoken queries recorded via microphone or uploaded audio files are fed into "
        "OpenAI Whisper (base model). Audio is normalized, resampled to 16,000 Hz 16-bit mono PCM, and transcribed with zero external API dependencies. "
        "The resulting text seamlessly integrates into the multi-turn conversational memory.",
        body_style
    ))

    # 5. Unit U4 — Text-to-Speech & Event Poster Generator
    story.append(Paragraph("5. Unit U4 — TTS Voice Synthesis & Event Poster Studio", h1_style))
    story.append(Paragraph(
        "<b>Text-to-Speech (TTS) Voice Engine:</b> Responses are converted to natural spoken audio via Google Text-to-Speech (gTTS) with "
        "an offline fallback to macOS native speech synthesizers. The TTS pre-processor cleans markdown asterisks, URLs, and code brackets "
        "to ensure smooth, pleasant auditory delivery.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Automated Publication Poster Studio:</b> When users inquire about departmental events (e.g., <i>AI-Conflux Hackathon</i> or "
        "<i>NeurOlympics</i>) or request promotional flyers, the high-resolution Pillow graphic engine renders a 1080&times;1440 publication poster. "
        "It features cybernetic grid overlays, typography hierarchies, highlight badges, venue cards, and a procedural registration QR code.",
        body_style
    ))

    # Poster Image Embedding
    poster_img_path = Path(__file__).resolve().parent / "outputs" / "posters" / "poster_ai-conflux2026.png"
    if poster_img_path.exists():
        story.append(KeepTogether([
            Paragraph("<b>Figure 2: Publication-Ready Event Poster Generated for Department Hackathon</b>", h2_style),
            Image(str(poster_img_path), width=3.2 * inch, height=4.2 * inch),
            Spacer(1, 8)
        ]))

    # 6. Unit U5 — Safety Guardrails, Refusal & Zero-PII Policy
    story.append(Paragraph("6. Unit U5 — Safety Guardrails, Hallucination Blocking & Zero-PII Policy", h1_style))
    story.append(Paragraph(
        "To ensure departmental compliance, strict three-tiered guardrails are enforced on every interaction:",
        body_style
    ))
    story.append(Paragraph(
        "• <b>Out-of-Scope Query Refusal:</b> Unrelated queries (politics, cooking recipes, sports, entertainment, personal counseling) "
        "are intercepted by regex classifiers and semantic distance checks, triggering an official academic refusal.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>Hallucination & Unsupported Answer Blocking:</b> If an in-domain question lacks grounding documentation in the FAQ database "
        "(confidence &lt; 0.35), the chatbot is strictly prevented from guessing or fabricating dates/numbers. It returns an official referral to Room 304.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>Zero Personal Data Retention (Anti-PII):</b> User inputs containing phone numbers, emails, credit cards, or government IDs "
        "are scrubbed in real-time (replaced with <code>[REDACTED_PHONE]</code>, <code>[REDACTED_EMAIL]</code>). No user data is ever written to disk.",
        bullet_style
    ))

    # 7. Verification & Unit Test Suite Matrix
    story.append(Paragraph("7. Comprehensive Test Suite Validation Matrix", h1_style))
    test_data = [
        ["Test Case / Unit", "Input Query / Action", "Expected Behavior", "Validation Status"],
        ["U1: System Prompt", "Inspect get_system_prompt()", "Contains persona, boundaries & tone", "✅ PASS (Verified)"],
        ["U2: Multi-Turn Memory", "2-turn sequential dialog", "Preserves history across sliding buffer", "✅ PASS (Verified)"],
        ["U2: LoRA Convergence", "4-Epoch PEFT training", "Loss drops 9.81 -> 6.17; PPL 18k -> 480", "✅ PASS (Verified)"],
        ["U3: Semantic Retrieval", "'How much attendance needed?'", "Cosine similarity > 0.50 for Doc #3", "✅ PASS (Score: 0.555)"],
        ["U3: Whisper STT", "16kHz Speech Input", "Transcribes clear voice prompt", "✅ PASS (Verified)"],
        ["U4: TTS Spoken Audio", "Synthesize department greeting", "Generates playable .mp3 audio file", "✅ PASS (Verified)"],
        ["U4: Poster Generator", "AI-Conflux Hackathon details", "Outputs 1080x1440 PNG graphic poster", "✅ PASS (Verified)"],
        ["U5: Out-of-Scope Refusal", "'How to bake a chocolate cake?'", "Polite refusal & scope clarification", "✅ PASS (Blocked)"],
        ["U5: Anti-PII Redaction", "Input: Phone & Email credentials", "Replaces with [REDACTED_*] tokens", "✅ PASS (Zero PII Saved)"],
        ["U5: Hallucination Blocker", "Ungrounded / made-up query", "Refuses fabrication; directs to HOD", "✅ PASS (Blocked)"]
    ]
    test_table = Table(test_data, colWidths=[1.3 * inch, 1.8 * inch, 2.5 * inch, 1.4 * inch])
    test_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 7.5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('FONTSIZE', (0,1), (-1,-1), 7),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#f8fafc")),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(test_table)
    story.append(Spacer(1, 10))

    # 8. Live App Universal URL & GitHub Link
    story.append(Paragraph("8. Live Application Universal URL & Deployment Guide", h1_style))
    story.append(Paragraph(
        "The project is structured for immediate worldwide access from any browser without complex firewall configurations:",
        body_style
    ))
    story.append(Paragraph(
        "• <b>Live Universal Application URL (Hugging Face Spaces Cloud):</b><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b><a href='https://huggingface.co/spaces/gladiatorspring/FAQChatbot'><font color='#059669'>https://huggingface.co/spaces/gladiatorspring/FAQChatbot</font></a></b><br/>"
        "Provides 24/7 high-availability cloud hosting with public HTTPS accessibility from any desktop, tablet, or smartphone worldwide.",
        body_style
    ))
    story.append(Paragraph(
        "• <b>Official GitHub Repository:</b><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b><a href='https://github.com/jeetdoesthings/FAQChatbot'><font color='#0284c7'>https://github.com/jeetdoesthings/FAQChatbot</font></a></b><br/>"
        "Contains complete source code, LoRA adapter weights, dataset JSON, test scripts, and demo instructions.",
        body_style
    ))

    # 9. Conclusion
    story.append(Paragraph("9. Conclusion", h1_style))
    conclusion_text = (
        "Project P24 successfully demonstrates a production-caliber Department FAQ Voice Chatbot satisfying all units U1 to U5. "
        "Through the fusion of dense Sentence-BERT retrieval, OpenAI Whisper speech recognition, LoRA parameter-efficient adaptation, "
        "speech synthesis, graphic design automation, and multi-layered safety guardrails, the chatbot delivers a responsive, reliable, "
        "and privacy-preserving virtual assistant for higher education departments."
    )
    story.append(Paragraph(conclusion_text, body_style))

    # Build document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[ReportGenerator] Successfully generated academic report at: {pdf_path}")
    return str(pdf_path)

if __name__ == "__main__":
    build_pdf_report("24_Jeet_P24.pdf")
