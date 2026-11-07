# 🎬 2–3 Minute Demo Video Walkthrough & Script

**Project Title:** P24 · Department FAQ Voice Chatbot  
**Candidate:** Jeet Ghegade | Roll No: 24 | Class: AIA 2 | Enrolment: ADT23SOCB0484  
**Target Duration:** 2 Minutes 30 Seconds  
**Live App URL:** [https://huggingface.co/spaces/gladiatorspring/FAQChatbot](https://huggingface.co/spaces/gladiatorspring/FAQChatbot)  
**Repository:** [https://github.com/jeetdoesthings/FAQChatbot](https://github.com/jeetdoesthings/FAQChatbot)

---

## ⏱️ Video Timeline & Scene Breakdown

### Scene 1: Introduction & Candidate Details (0:00 – 0:25)
- **Visual:** Show browser with Web App header or slide displaying:
  - Name: Jeet Ghegade
  - Roll No: 24 | Class: AIA 2 | Enrolment: ADT23SOCB0484
  - Project: P24 · Department FAQ Voice Chatbot
  - GitHub Link: `https://github.com/jeetdoesthings/FAQChatbot`
- **Spoken Script:**
  > "Hello everyone, my name is Jeet Ghegade, Roll No 24 from Class AIA 2, Enrolment number ADT23SOCB0484. Today I am presenting my Generative AI project: P24 - Department FAQ Voice Chatbot. This system provides conversational answers to department FAQs by text and voice over multiple turns, featuring Sentence-BERT semantic retrieval, Whisper speech-to-text, LoRA domain fine-tuning, Text-to-Speech audio, automated event-poster generation, and strict privacy guardrails."

---

### Scene 2: Voice Input & Multi-Turn Spoken Interaction (0:25 – 1:05)
- **Visual:** 
  1. Click the microphone icon in the Web App interface.
  2. Speak: *"What are the eligibility criteria and fees for the B.Tech AI program?"*
  3. Click **"Transcribe & Ask 🎙️"**.
  4. Point out Whisper STT transcription appearing in chat.
  5. Play the synthesized TTS audio response.
  6. Ask a follow-up multi-turn question: *"What is the department attendance policy for writing semester exams?"*
  7. Show how the chatbot retains context in multi-turn memory and returns the verified 75% policy with match confidence.
- **Spoken Script:**
  > "First, let's test voice input. I record my voice asking about B.Tech eligibility and tuition fees. OpenAI Whisper transcribes the audio, and Sentence-BERT indexes and retrieves the official knowledge base entry. The bot responds both in text and generates a fluent spoken response using TTS. In the second turn, I test conversational memory with a follow-up query on attendance rules, which is retrieved with over 90% confidence."

---

### Scene 3: Event Poster Generator (1:05 – 1:40)
- **Visual:**
  1. Switch to the **Event Poster Studio** tab (or type *"Generate an event poster for the AI-Conflux Hackathon"*).
  2. Show the customizable parameters: Event Title, Tagline, Date, Venue, Highlights, and Theme ("Cyber Deep Blue").
  3. Click **"Generate Event Poster 🎨"**.
  4. Showcase the generated high-resolution 1080x1440 publication poster complete with futuristic matrix styling, category badges, venue schedule, and registration QR code.
- **Spoken Script:**
  > "Next is Unit U4's Event Poster Generator. When students or department coordinators need promotional graphics for department events like our annual AI-Conflux Hackathon or NeurOlympics, the poster engine generates a high-resolution, publication-ready vertical poster featuring gradient typography, date and venue cards, cash prize highlights, and a registration QR code."

---

### Scene 4: Safety Guardrails & Privacy (1:40 – 2:10)
- **Visual:**
  1. Test Out-of-Scope query: Type *"How do I bake a chocolate cake at home?"*
  2. Show the bot immediately refusing the request with the official department persona.
  3. Test PII Guardrail: Type *"My phone number is 9876543210 and email is test@xyz.com. Can you save my info?"*
  4. Show the telemetry box displaying: `[REDACTED_PHONE]` and `[REDACTED_EMAIL]` with zero personal data stored.
- **Spoken Script:**
  > "Unit U5 enforces strict guardrails. When asked an unrelated question like cooking or politics, the bot politely refuses and clarifies its departmental scope. Furthermore, to adhere to privacy guidelines, whenever personal details such as phone numbers or emails are submitted, our regex and privacy filters redact them on the fly, guaranteeing zero personal data retention."

---

### Scene 5: LoRA Metrics, Architecture & Conclusion (2:10 – 2:30)
- **Visual:**
  1. Switch to the **System Architecture & Metrics** tab.
  2. Show the LoRA loss curve plot (`outputs/lora_training_loss.png`).
  3. Point out: Only 0.18% trainable parameters, with loss dropping from 9.81 down to 6.17 and perplexity from 18,281 to 480.
  4. Display the GitHub repository and live application URL.
- **Spoken Script:**
  > "Finally, we fine-tuned our language model using LoRA with rank 8 on our department FAQ corpus, training only 0.18% of parameters and achieving massive convergence. The complete codebase is published on GitHub at jeetdoesthings/FAQChatbot with automated test suites passing. Thank you!"

---

## 🛠️ How to Record Your Video on Mac in 3 Easy Steps:
1. Press `Cmd + Shift + 5` to open macOS built-in screen recorder.
2. Select your microphone in **Options** and click **Record Entire Screen** or **Selected Portion**.
3. Run `python3 app.py` (or `python3 app.py --share`) and follow the 5 scenes above.
4. Save the video as `24_Jeet_P24_demo.mp4` (2 to 3 minutes).
