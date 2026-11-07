"""
LoRA Fine-Tuning Pipeline for Department FAQ Domain Adaptation (Unit U2)
Fine-tunes a causal language model using Parameter-Efficient Fine-Tuning (PEFT / LoRA).
Saves adapter weights, computes perplexity metrics, and exports loss curves.
"""
import os
os.environ["USE_TF"] = "0"
os.environ["TRANSFORMERS_NO_TF"] = "1"

import json
import time
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from typing import List, Dict, Any, Tuple
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import LoraConfig, get_peft_model, TaskType, PeftModel

from src.config import BASE_MODEL_NAME, LORA_DATASET_PATH, LORA_OUTPUT_DIR, OUTPUT_DIR

class FAQDataset(Dataset):
    def __init__(self, data_path: Path, tokenizer, max_length: int = 256):
        self.samples = []
        with open(data_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    item = json.loads(line)
                    # Format as standard instruction prompt
                    formatted_text = (
                        f"<|system|>\nYou are an official Department FAQ Assistant.\n"
                        f"<|user|>\n{item['input']}\n"
                        f"<|assistant|>\n{item['output']}<|endoftext|>"
                    )
                    self.samples.append(formatted_text)

        self.encodings = tokenizer(
            self.samples,
            truncation=True,
            max_length=max_length,
            padding="max_length",
            return_tensors="pt"
        )

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        item = {key: val[idx] for key, val in self.encodings.items()}
        item["labels"] = item["input_ids"].clone()
        return item

def train_lora_faq(
    model_name: str = BASE_MODEL_NAME,
    dataset_path: Path = LORA_DATASET_PATH,
    output_dir: Path = LORA_OUTPUT_DIR,
    epochs: int = 5,
    lr: float = 3e-4,
    batch_size: int = 2,
    lora_r: int = 8,
    lora_alpha: int = 16
) -> Dict[str, Any]:
    """
    Executes LoRA fine-tuning on the FAQ corpus.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    device = torch.device("mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu")
    print(f"[LoRA Training] Using device: {device}")

    # 1. Load Tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # 2. Load Base Model
    print(f"[LoRA Training] Loading base model '{model_name}'...")
    base_model = AutoModelForCausalLM.from_pretrained(model_name)
    base_model.to(device)

    # Calculate initial baseline loss
    dataset = FAQDataset(dataset_path, tokenizer)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    base_model.eval()
    init_loss = 0.0
    with torch.no_grad():
        for batch in dataloader:
            b_ids = batch["input_ids"].to(device)
            b_mask = batch["attention_mask"].to(device)
            b_labels = batch["labels"].to(device)
            loss = base_model(input_ids=b_ids, attention_mask=b_mask, labels=b_labels).loss
            init_loss += loss.item()
    init_loss /= len(dataloader)
    init_ppl = math.exp(min(init_loss, 20.0))
    print(f"[LoRA Training] Initial Base Model Loss: {init_loss:.4f} | Perplexity: {init_ppl:.2f}")

    # 3. Apply LoRA Config
    peft_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=lora_r,
        lora_alpha=lora_alpha,
        lora_dropout=0.05,
        target_modules=["c_attn"],
        bias="none"
    )
    lora_model = get_peft_model(base_model, peft_config)
    trainable_params, all_param = lora_model.get_nb_trainable_parameters()
    pct = 100 * trainable_params / all_param
    print(f"[LoRA Training] Trainable params: {trainable_params:,} || All params: {all_param:,} || {pct:.2f}%")

    # 4. Optimizer & Training Loop
    optimizer = torch.optim.AdamW(lora_model.parameters(), lr=lr, weight_decay=0.01)
    loss_history = []
    epoch_losses = []

    print(f"[LoRA Training] Starting fine-tuning for {epochs} epochs...")
    lora_model.train()
    start_time = time.time()

    for epoch in range(1, epochs + 1):
        running_loss = 0.0
        for step, batch in enumerate(dataloader):
            b_ids = batch["input_ids"].to(device)
            b_mask = batch["attention_mask"].to(device)
            b_labels = batch["labels"].to(device)

            optimizer.zero_grad()
            outputs = lora_model(input_ids=b_ids, attention_mask=b_mask, labels=b_labels)
            loss = outputs.loss
            loss.backward()
            torch.nn.utils.clip_grad_norm_(lora_model.parameters(), 1.0)
            optimizer.step()

            running_loss += loss.item()
            loss_history.append(loss.item())

        ep_loss = running_loss / len(dataloader)
        epoch_losses.append(ep_loss)
        print(f"  Epoch {epoch}/{epochs} - Loss: {ep_loss:.4f}")

    elapsed_time = round(time.time() - start_time, 2)
    final_loss = epoch_losses[-1]
    final_ppl = math.exp(min(final_loss, 20.0))
    print(f"[LoRA Training] Completed in {elapsed_time}s | Final Loss: {final_loss:.4f} | Final Perplexity: {final_ppl:.2f}")

    # 5. Save Adapter
    print(f"[LoRA Training] Saving LoRA adapter to {output_dir}...")
    lora_model.save_pretrained(str(output_dir))
    tokenizer.save_pretrained(str(output_dir))

    # 6. Save Metrics
    metrics = {
        "base_model": model_name,
        "dataset_samples": len(dataset),
        "epochs": epochs,
        "lora_rank": lora_r,
        "lora_alpha": lora_alpha,
        "trainable_params": trainable_params,
        "all_params": all_param,
        "trainable_percentage": round(pct, 2),
        "initial_loss": round(init_loss, 4),
        "final_loss": round(final_loss, 4),
        "initial_perplexity": round(init_ppl, 2),
        "final_perplexity": round(final_ppl, 2),
        "training_time_seconds": elapsed_time,
        "epoch_losses": [round(l, 4) for l in epoch_losses]
    }

    metrics_path = output_dir / "training_metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    # 7. Render and save loss curve
    plot_path = OUTPUT_DIR / "lora_training_loss.png"
    plt.figure(figsize=(8, 4.5), dpi=150)
    plt.plot(range(1, len(loss_history) + 1), loss_history, marker='o', color='#3b82f6', label='Step Loss')
    plt.title(f"LoRA Adaptation Convergence on Department FAQs\nInitial Loss: {init_loss:.2f} -> Final Loss: {final_loss:.2f}")
    plt.xlabel("Optimization Steps")
    plt.ylabel("Cross-Entropy Loss")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig(str(plot_path))
    plt.close()
    print(f"[LoRA Training] Saved loss curve plot to: {plot_path}")

    return metrics

if __name__ == "__main__":
    train_lora_faq(epochs=4)
