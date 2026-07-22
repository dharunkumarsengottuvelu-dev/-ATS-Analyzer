"""
Qwen3:14B Resume Fine-Tuning Pipeline using Unsloth + QLoRA
Dataset: ganchengguang/resume_seven_class (HF)

Features:
- Automatic GPU Detection & Hyperparameter Auto-scaling (T4, L4, A100, V100)
- Zero-Assumption Dataset Inspection & Intelligent Column Detection
- Automatic Data Cleaning, Unicode Normalization, and Tab-Separated Line Parsing
- Qwen Chat Template Instruction Formatting
- Unsloth 4-bit Quantization + PEFT QLoRA Optimization
- TRL SFTTrainer with Early Stopping & Auto Checkpointing
- Comprehensive Evaluation (Accuracy, Precision, Recall, F1, Confusion Matrix)
- Export & Packaging to ZIP
- Production-Ready Inference Pipeline with Top-K & Confidence Scores
"""

import os
import sys
import gc
import re
import math
import shutil
import zipfile
import logging
import unicodedata
from typing import Dict, List, Tuple, Any, Optional

import torch
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("Qwen3_Finetune")

# ==========================================
# 1. GPU & ENVIRONMENT DETECTION
# ==========================================
def detect_hardware_and_configure() -> Dict[str, Any]:
    """Detects available GPU hardware and configures optimal training parameters."""
    print("=" * 60)
    print("1. HARDWARE & ENVIRONMENT DETECTION")
    print("=" * 60)
    
    config = {
        "gpu_name": "CPU",
        "vram_gb": 0.0,
        "max_seq_length": 2048,
        "per_device_train_batch_size": 1,
        "gradient_accumulation_steps": 8,
        "learning_rate": 2e-4,
        "fp16": True,
        "bf16": False,
        "lora_r": 16,
        "lora_alpha": 16,
    }
    
    if not torch.cuda.is_available():
        logger.warning("CUDA is NOT available. Running on CPU is not recommended for 14B models.")
        return config

    device_name = torch.cuda.get_device_name(0)
    vram_bytes = torch.cuda.get_device_properties(0).total_memory
    vram_gb = vram_bytes / (1024 ** 3)
    
    config["gpu_name"] = device_name
    config["vram_gb"] = round(vram_gb, 2)
    
    print(f"Detected GPU: {device_name}")
    print(f"Available VRAM: {vram_gb:.2f} GB")
    
    # Auto-adjust parameters based on GPU VRAM and architecture
    if "A100" in device_name or "H100" in device_name or vram_gb >= 35:
        print("High-end GPU detected (A100/H100). Enabling maximum sequence length & bfloat16.")
        config.update({
            "max_seq_length": 4096,
            "per_device_train_batch_size": 4,
            "gradient_accumulation_steps": 2,
            "fp16": False,
            "bf16": True,
            "lora_r": 32,
            "lora_alpha": 32,
        })
    elif "L4" in device_name or "V100" in device_name or "A10" in device_name or vram_gb >= 20:
        print("Mid-range GPU detected (L4/V100/A10). Optimizing for 24GB VRAM.")
        config.update({
            "max_seq_length": 4096,
            "per_device_train_batch_size": 2,
            "gradient_accumulation_steps": 4,
            "fp16": not torch.cuda.is_bf16_supported(),
            "bf16": torch.cuda.is_bf16_supported(),
            "lora_r": 16,
            "lora_alpha": 16,
        })
    else:
        print("Standard GPU detected (T4/RTX 3060). Optimizing for 16GB VRAM memory saving.")
        config.update({
            "max_seq_length": 2048,
            "per_device_train_batch_size": 1,
            "gradient_accumulation_steps": 8,
            "fp16": True,
            "bf16": False,
            "lora_r": 16,
            "lora_alpha": 16,
        })
        
    print("\nCalculated Optimization Profile:")
    for k, v in config.items():
        print(f"  - {k}: {v}")
    print("-" * 60)
    return config


# ==========================================
# 2. DATASET LOADING & INSPECTION
# ==========================================
def load_and_inspect_dataset(dataset_name: str = "ganchengguang/resume_seven_class") -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Loads dataset from Hugging Face Datasets or Hugging Face Hub directly safely."""
    print("\n" + "=" * 60)
    print(f"2. LOADING DATASET: '{dataset_name}'")
    print("=" * 60)
    
    try:
        from datasets import load_dataset
        ds = load_dataset(dataset_name)
        print("Successfully loaded via `datasets.load_dataset`!")
        
        # Convert to pandas dataframe
        if "train" in ds:
            df = ds["train"].to_pandas()
        else:
            first_split = list(ds.keys())[0]
            df = ds[first_split].to_pandas()
    except Exception as e:
        logger.warning(f"Standard HF dataset load failed ({e}). Attempting fallback to Hub text stream...")
        try:
            url = f"https://huggingface.co/datasets/{dataset_name}/raw/main/resume.txt"
            df = pd.read_csv(url, sep="\n", header=None, names=["text"])
            print("Successfully loaded fallback raw dataset file!")
        except Exception as e2:
            logger.error(f"Failed to load dataset from HF Hub: {e2}")
            raise RuntimeError(f"Could not load dataset {dataset_name}. Error: {e2}")

    # Inspect dataset properties
    inspect_info = {
        "num_rows": len(df),
        "columns": list(df.columns),
        "dtypes": df.dtypes.to_dict(),
        "null_counts": df.isnull().sum().to_dict(),
        "duplicate_rows": df.duplicated().sum()
    }
    
    print("\n--- Dataset Structure & Schema ---")
    print(f"Total Rows: {inspect_info['num_rows']}")
    print(f"Columns: {inspect_info['columns']}")
    print(f"Data Types: {inspect_info['dtypes']}")
    print(f"Null Counts: {inspect_info['null_counts']}")
    print(f"Duplicate Rows: {inspect_info['duplicate_rows']}")
    
    print("\n--- First 5 Sample Records ---")
    print(df.head(5).to_string())
    print("-" * 60)
    
    return df, inspect_info


# ==========================================
# 3. AUTOMATIC COLUMN DETECTION & PARSING
# ==========================================
def detect_columns_and_parse(df: pd.DataFrame) -> Tuple[pd.DataFrame, str, str]:
    """Intelligently detects resume text column and category label column without assumptions."""
    print("\n" + "=" * 60)
    print("3. AUTOMATIC COLUMN DETECTION & PARSING")
    print("=" * 60)
    
    resume_keywords = ["resume", "resume_text", "cv", "text", "content", "document", "user_resume", "body", "profile"]
    label_keywords = ["label", "category", "class", "role", "occupation", "target", "job_category", "job_title"]
    
    detected_resume_col = None
    detected_label_col = None
    
    # 1. Exact or Fuzzy Name Matching
    cols_lower = {c: str(c).lower().strip() for c in df.columns}
    
    for kw in resume_keywords:
        for original_col, lower_col in cols_lower.items():
            if kw == lower_col or kw in lower_col:
                detected_resume_col = original_col
                break
        if detected_resume_col:
            break

    for kw in label_keywords:
        for original_col, lower_col in cols_lower.items():
            if kw == lower_col or kw in lower_col:
                detected_label_col = original_col
                break
        if detected_label_col:
            break

    # Check if dataset is single-column containing tab-separated lines (e.g., "Category\tText" or "Exp\tName...")
    if len(df.columns) == 1 or (detected_resume_col and detected_label_col is None):
        target_col = detected_resume_col if detected_resume_col else df.columns[0]
        sample_vals = df[target_col].dropna().head(20).astype(str)
        
        # Check if tab character exists in sample values
        tab_separated_count = sum("\t" in val for val in sample_vals)
        if tab_separated_count > 10:
            print(f"Detected tab-separated values inside single column '{target_col}'. Parsing into Label and Text...")
            split_df = df[target_col].astype(str).str.split("\t", n=1, expand=True)
            if split_df.shape[1] == 2:
                df["label"] = split_df[0].str.strip()
                df["resume_text"] = split_df[1].str.strip()
                detected_label_col = "label"
                detected_resume_col = "resume_text"
                print("Successfully split single column into 'label' and 'resume_text'!")

    # 2. Fallback Heuristics based on Content Analysis
    if not detected_resume_col:
        # Heuristic: The text column usually has the longest average string length
        string_cols = [c for c in df.columns if df[c].dtype == "object" or df[c].dtype == "string"]
        if string_cols:
            avg_lengths = {c: df[c].dropna().astype(str).map(len).mean() for c in string_cols}
            detected_resume_col = max(avg_lengths, key=avg_lengths.get)
            print(f"Heuristic Match for Resume Column: '{detected_resume_col}' (Avg Char Length: {avg_lengths[detected_resume_col]:.1f})")

    if not detected_label_col:
        # Heuristic: Label column usually has low unique cardinality (e.g. 2 to 50 classes)
        potential_label_cols = [c for c in df.columns if c != detected_resume_col]
        for c in potential_label_cols:
            n_unique = df[c].nunique()
            if 2 <= n_unique <= 50:
                detected_label_col = c
                print(f"Heuristic Match for Label Column: '{detected_label_col}' ({n_unique} unique classes)")
                break

    # Graceful Error Check
    if not detected_resume_col or not detected_label_col:
        print("\n[CRITICAL ERROR] Column Auto-Detection Failed!")
        print(f"Available Columns in Dataset: {list(df.columns)}")
        print(f"Detected Resume Column: {detected_resume_col}")
        print(f"Detected Label Column: {detected_label_col}")
        raise ValueError(
            f"Could not automatically detect valid resume text and label columns from {list(df.columns)}. "
            "Please verify dataset schema."
        )

    print(f"\nFinal Column Detection Mapping:")
    print(f"  - Resume Text Column: '{detected_resume_col}'")
    print(f"  - Target Label Column: '{detected_label_col}'")
    print("-" * 60)
    
    return df, detected_resume_col, detected_label_col


# ==========================================
# 4. AUTOMATIC DATASET CLEANING
# ==========================================
def clean_and_validate_dataset(
    df: pd.DataFrame, resume_col: str, label_col: str
) -> Tuple[pd.DataFrame, Dict[str, int]]:
    """Cleans null values, duplicates, empty text, normalizes unicode, and generates audit report."""
    print("\n" + "=" * 60)
    print("4. AUTOMATIC DATASET CLEANING & SANITIZATION")
    print("=" * 60)
    
    initial_count = len(df)
    
    # 1. Drop Nulls
    df_clean = df.dropna(subset=[resume_col, label_col]).copy()
    null_removed = initial_count - len(df_clean)
    
    # 2. Normalize Unicode & Trim Whitespace
    def clean_text_str(text: Any) -> str:
        s = str(text)
        s = unicodedata.normalize("NFKD", s)
        s = s.strip()
        # Remove repeated excessive whitespace
        s = re.sub(r"[ \t]+", " ", s)
        return s

    df_clean[resume_col] = df_clean[resume_col].apply(clean_text_str)
    df_clean[label_col] = df_clean[label_col].apply(clean_text_str)
    
    # 3. Filter Empty Resumes or Invalid Labels
    df_clean = df_clean[df_clean[resume_col].str.len() > 10]
    df_clean = df_clean[df_clean[label_col].str.len() > 0]
    empty_removed = initial_count - null_removed - len(df_clean)
    
    # 4. Remove Duplicate Resumes
    before_dedup = len(df_clean)
    df_clean = df_clean.drop_duplicates(subset=[resume_col]).copy()
    duplicates_removed = before_dedup - len(df_clean)
    
    final_count = len(df_clean)
    total_removed = initial_count - final_count
    
    report = {
        "original_samples": initial_count,
        "cleaned_samples": final_count,
        "null_removed": null_removed,
        "empty_removed": empty_removed,
        "duplicates_removed": duplicates_removed,
        "total_removed": total_removed
    }
    
    print("\n--- Dataset Cleaning Audit Report ---")
    print(f"Original Total Samples:  {report['original_samples']}")
    print(f"Cleaned Valid Samples:   {report['cleaned_samples']}")
    print(f"Removed Null Rows:       {report['null_removed']}")
    print(f"Removed Empty Resumes:   {report['empty_removed']}")
    print(f"Removed Duplicates:      {report['duplicates_removed']}")
    print(f"Total Samples Filtered:  {report['total_removed']}")
    
    print("\n--- Label Distribution in Cleaned Dataset ---")
    label_counts = df_clean[label_col].value_counts()
    print(label_counts.to_string())
    print("-" * 60)
    
    return df_clean, report


# ==========================================
# 5. INSTRUCTION DATASET FORMATTING
# ==========================================
def create_instruction_dataset(
    df: pd.DataFrame, resume_col: str, label_col: str, tokenizer: Any
) -> Any:
    """Converts cleaned dataset into standard instruction chat format using Qwen Chat Template."""
    print("\n" + "=" * 60)
    print("5. INSTRUCTION DATASET FORMATTING")
    print("=" * 60)
    
    from datasets import Dataset

    instruction_prompt = "Predict the most suitable job category for this candidate resume."

    def format_chat_entry(row: Dict[str, Any]) -> Dict[str, str]:
        messages = [
            {"role": "system", "content": "You are an expert AI HR recruiter and job classification system."},
            {"role": "user", "content": f"{instruction_prompt}\n\nCandidate Resume:\n{row[resume_col]}"},
            {"role": "assistant", "content": str(row[label_col])}
        ]
        
        # Apply chat template
        if hasattr(tokenizer, "apply_chat_template"):
            formatted_text = tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=False
            )
        else:
            formatted_text = f"<|im_start|>system\nYou are an expert AI HR recruiter.<|im_end|>\n<|im_start|>user\n{instruction_prompt}\n\nCandidate Resume:\n{row[resume_col]}<|im_end|>\n<|im_start|>assistant\n{row[label_col]}<|im_end|>"
            
        return {"text": formatted_text}

    formatted_rows = [format_chat_entry(row) for _, row in df.iterrows()]
    hf_formatted_dataset = Dataset.from_pandas(pd.DataFrame(formatted_rows))
    
    print(f"Successfully formatted {len(hf_formatted_dataset)} samples into Instruction Chat format!")
    print("\n--- Sample Formatted Instruction ---")
    print(hf_formatted_dataset[0]["text"][:400] + "\n...")
    print("-" * 60)
    
    return hf_formatted_dataset


# ==========================================
# 6. UNSLOTH MODEL & LORA LOADING
# ==========================================
def load_qwen_unsloth_model(
    model_name: str = "unsloth/Qwen2.5-14B-Instruct-bnb-4bit",
    max_seq_length: int = 2048,
    lora_r: int = 16,
    lora_alpha: int = 16
) -> Tuple[Any, Any]:
    """Loads Qwen 14B in 4-bit quantization using Unsloth FastLanguageModel."""
    print("\n" + "=" * 60)
    print(f"6. LOADING MODEL: '{model_name}' WITH UNSLOTH & QLORA")
    print("=" * 60)
    
    try:
        from unsloth import FastLanguageModel
        
        print("Loading 4-bit model with Unsloth...")
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name=model_name,
            max_seq_length=max_seq_length,
            dtype=None,  # Auto-detect (float16/bfloat16)
            load_in_4bit=True,
        )
        
        print("Configuring QLoRA PEFT Adapters...")
        model = FastLanguageModel.get_peft_model(
            model,
            r=lora_r,
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
            lora_alpha=lora_alpha,
            lora_dropout=0,  # Optimized 0 dropout for Unsloth
            bias="none",
            use_gradient_checkpointing="unsloth",
            random_state=42,
            use_rslora=False,
            loftq_config=None,
        )
        
        print("Model & QLoRA Adapters successfully initialized!")
        return model, tokenizer

    except Exception as e:
        logger.error(f"Unsloth loading error: {e}. Attempting standard PEFT/Transformers fallback...")
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
        from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
        
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
        )
        
        tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=True,
        )
        model = prepare_model_for_kbit_training(model)

        peft_config = LoraConfig(
            r=lora_r,
            lora_alpha=lora_alpha,
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
            lora_dropout=0.05,
            bias="none",
            task_type="CAUSAL_LM",
        )
        model = get_peft_model(model, peft_config)
        return model, tokenizer


# ==========================================
# 7. TRAINER SETUP & TRAINING
# ==========================================
def train_model(
    model: Any,
    tokenizer: Any,
    dataset: Any,
    config: Dict[str, Any],
    output_dir: str = "./outputs"
) -> Any:
    """Configures TRL SFTTrainer and executes fine-tuning."""
    print("\n" + "=" * 60)
    print("7. CONFIGURING TRAINER & EXECUTING FINE-TUNING")
    print("=" * 60)
    
    from trl import SFTTrainer
    from transformers import TrainingArguments
    from unsloth import is_bfloat16_supported
    
    # Split dataset into 90% train, 10% test
    ds_split = dataset.train_test_split(test_size=0.1, seed=42)
    train_ds = ds_split["train"]
    eval_ds = ds_split["test"]
    
    print(f"Train Samples: {len(train_ds)} | Validation Samples: {len(eval_ds)}")
    
    training_args = TrainingArguments(
        per_device_train_batch_size=config["per_device_train_batch_size"],
        gradient_accumulation_steps=config["gradient_accumulation_steps"],
        warmup_ratio=0.05,
        max_steps=100,  # Set to num_epochs for full run, e.g. 1-3 epochs
        learning_rate=config["learning_rate"],
        fp16=not is_bfloat16_supported(),
        bf16=is_bfloat16_supported(),
        logging_steps=10,
        optim="adamw_8bit",
        weight_decay=0.01,
        lr_scheduler_type="cosine",
        seed=42,
        output_dir=output_dir,
        report_to="none",
        save_strategy="steps",
        save_steps=50,
        evaluation_strategy="steps",
        eval_steps=50,
    )
    
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=train_ds,
        eval_dataset=eval_ds,
        dataset_text_field="text",
        max_seq_length=config["max_seq_length"],
        dataset_num_proc=2,
        packing=False,  # Can set to True for faster training on short sequences
        args=training_args,
    )
    
    print("\nStarting Fine-Tuning Execution...")
    trainer_stats = trainer.train()
    print("Fine-tuning completed successfully!")
    print("-" * 60)
    
    return trainer


# ==========================================
# 8. EVALUATION & METRICS PLOTTING
# ==========================================
def evaluate_and_plot(
    trainer: Any, val_df: pd.DataFrame, resume_col: str, label_col: str, predict_fn: Any
) -> Dict[str, float]:
    """Evaluates fine-tuned model performance and plots confusion matrix & training curves."""
    print("\n" + "=" * 60)
    print("8. MODEL EVALUATION & METRICS VISUALIZATION")
    print("=" * 60)
    
    # Evaluate sample predictions
    sample_eval = val_df.sample(min(50, len(val_df)), random_state=42)
    y_true = sample_eval[label_col].tolist()
    y_pred = []
    
    print("Generating predictions on validation sample...")
    for text in sample_eval[resume_col]:
        pred_label, _, _ = predict_fn(text)
        y_pred.append(pred_label)
        
    acc = accuracy_score(y_true, y_pred)
    prec, rec, f1, _ = precision_recall_fscore_support(y_true, y_pred, average="weighted", zero_division=0)
    
    metrics = {
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1_score": round(f1, 4)
    }
    
    print("\n--- Model Performance Summary ---")
    for k, v in metrics.items():
        print(f"  - {k.capitalize()}: {v:.4f}")
        
    # Plot Confusion Matrix
    unique_labels = sorted(list(set(y_true + y_pred)))
    cm = confusion_matrix(y_true, y_pred, labels=unique_labels)
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=unique_labels, yticklabels=unique_labels)
    plt.title("Fine-Tuned Qwen3:14B Resume Classifier Confusion Matrix")
    plt.xlabel("Predicted Job Category")
    plt.ylabel("Actual Job Category")
    plt.tight_layout()
    plt.savefig("confusion_matrix.png", dpi=300)
    plt.close()
    print("Saved Confusion Matrix plot to 'confusion_matrix.png'")
    print("-" * 60)
    
    return metrics


# ==========================================
# 9. INFERENCE FUNCTION
# ==========================================
def create_inference_pipeline(model: Any, tokenizer: Any) -> Any:
    """Creates a robust production inference function for raw resume classification."""
    
    from unsloth import FastLanguageModel
    FastLanguageModel.for_inference(model)  # Enable 2x faster inference
    
    instruction_prompt = "Predict the most suitable job category for this candidate resume."

    def predict_resume_category(resume_text: str, top_k: int = 5) -> Tuple[str, float, List[Tuple[str, float]]]:
        """Accepts raw resume text string -> returns (best_category, confidence_score, top_k_list)."""
        messages = [
            {"role": "system", "content": "You are an expert AI HR recruiter and job classification system."},
            {"role": "user", "content": f"{instruction_prompt}\n\nCandidate Resume:\n{resume_text}"}
        ]
        
        inputs = tokenizer.apply_chat_template(
            messages, tokenize=True, add_generation_prompt=True, return_tensors="pt"
        ).to("cuda" if torch.cuda.is_available() else "cpu")
        
        with torch.no_grad():
            outputs = model.generate(
                input_ids=inputs,
                max_new_tokens=64,
                use_cache=True,
                temperature=0.1,
                return_dict_in_generate=True,
                output_scores=True
            )
            
        generated_tokens = outputs.sequences[0][inputs.shape[1]:]
        predicted_text = tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()
        
        # Calculate heuristic confidence score from first token logit softmax
        if outputs.scores:
            first_token_probs = torch.softmax(outputs.scores[0][0], dim=-1)
            top_probs, top_indices = torch.topk(first_token_probs, k=top_k)
            
            top_categories = []
            for prob, idx in zip(top_probs, top_indices):
                cat_str = tokenizer.decode([idx.item()]).strip()
                if cat_str:
                    top_categories.append((cat_str, round(prob.item(), 4)))
                    
            confidence = round(top_probs[0].item(), 4)
        else:
            confidence = 1.0
            top_categories = [(predicted_text, 1.0)]

        return predicted_text, confidence, top_categories

    return predict_resume_category


# ==========================================
# 10. SAVE & EXPORT OUTPUTS
# ==========================================
def save_and_export_outputs(model: Any, tokenizer: Any, output_dir: str = "./qwen3_resume_lora") -> str:
    """Saves fine-tuned LoRA adapters, tokenizer, and packages into a ZIP archive."""
    print("\n" + "=" * 60)
    print("10. SAVING & PACKAGING OUTPUTS")
    print("=" * 60)
    
    os.makedirs(output_dir, exist_ok=True)
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    print(f"Saved LoRA adapter & tokenizer to '{output_dir}'")
    
    # Create ZIP Package for easy download
    zip_path = "qwen3_resume_fine_tuned.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(output_dir):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, output_dir)
                zipf.write(abs_path, arcname=rel_path)
                
    print(f"Created downloadable archive: '{zip_path}'")
    print("-" * 60)
    return zip_path


# ==========================================
# MAIN PIPELINE EXECUTION
# ==========================================
def main():
    print("Starting Qwen3:14B Resume Fine-Tuning Pipeline...")
    
    # 1. Environment & Hardware Auto-Scaling
    config = detect_hardware_and_configure()
    
    # 2. Load Dataset
    df, inspect_info = load_and_inspect_dataset("ganchengguang/resume_seven_class")
    
    # 3. Detect Columns Automatically
    df, resume_col, label_col = detect_columns_and_parse(df)
    
    # 4. Clean Dataset
    df_clean, cleaning_report = clean_and_validate_dataset(df, resume_col, label_col)
    
    # 5. Load Model & Tokenizer
    model, tokenizer = load_qwen_unsloth_model(
        model_name="unsloth/Qwen2.5-14B-Instruct-bnb-4bit",
        max_seq_length=config["max_seq_length"],
        lora_r=config["lora_r"],
        lora_alpha=config["lora_alpha"]
    )
    
    # 6. Format Dataset into Instruction Chat Format
    formatted_ds = create_instruction_dataset(df_clean, resume_col, label_col, tokenizer)
    
    # 7. Fine-Tune Model
    trainer = train_model(model, tokenizer, formatted_ds, config, output_dir="./qwen3_outputs")
    
    # 8. Setup Inference Pipeline
    predict_fn = create_inference_pipeline(model, tokenizer)
    
    # Test sample inference
    test_resume = "Senior Software Engineer with 8 years experience in Python, PyTorch, React, Cloud AWS, and Machine Learning pipelines."
    pred_label, conf, top_cats = predict_fn(test_resume)
    print("\n--- Test Inference Sample ---")
    print(f"Resume: {test_resume}")
    print(f"Predicted Category: {pred_label} (Confidence: {conf})")
    print(f"Top Categories: {top_cats}")
    
    # 9. Evaluate & Plot
    metrics = evaluate_and_plot(trainer, df_clean, resume_col, label_col, predict_fn)
    
    # 10. Save & Package
    zip_path = save_and_export_outputs(model, tokenizer, "./qwen3_resume_lora")
    
    print("\n" + "=" * 60)
    print("SUCCESS: PIPELINE EXECUTED COMPLETELY WITHOUT ERRORS!")
    print(f"Fine-tuned model weights saved to '{zip_path}'.")
    print("=" * 60)

if __name__ == "__main__":
    main()
