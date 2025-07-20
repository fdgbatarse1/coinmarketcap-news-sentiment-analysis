from loguru import logger
import torch
import numpy as np
import pandas as pd
from datasets import load_dataset
from transformers import (
    pipeline,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
    AutoModelForSequenceClassification,
)
from sklearn.metrics import balanced_accuracy_score, accuracy_score


def sentiment_analysis():
    logger.info("Starting sentiment analysis...")

    model_name = "yiyanghkust/finbert-tone"

    if torch.cuda.is_available():
        logger.info("CUDA available. GPU will be used for computation.")
        device = 0
    else:
        logger.info("CUDA not available. Using CPU for computation.")
        device = -1

    sentiment_pipeline = pipeline(
        task="sentiment-analysis", model=model_name, batch_size=128, device=device
    )

    result = sentiment_pipeline("I love you")

    logger.info(result)

    ds = load_dataset("juanka0357/bitcoin-sentiment-analysis")

    full_dataset = ds["train"]

    total_samples = len(full_dataset)
    train_size = int(0.6 * total_samples)
    val_size = int(0.2 * total_samples)
    test_size = total_samples - train_size - val_size

    ds_train = full_dataset.select(range(train_size))
    ds_val = full_dataset.select(range(train_size, train_size + val_size))
    ds_test = full_dataset.select(
        range(train_size + val_size, train_size + val_size + test_size)
    )

    tokenizer = AutoTokenizer.from_pretrained(model_name)

    ds_train = ds_train.rename_column("output", "labels")
    ds_val = ds_val.rename_column("output", "labels")
    ds_test = ds_test.rename_column("output", "labels")

    ds_train = ds_train.rename_column("input", "text")
    ds_val = ds_val.rename_column("input", "text")
    ds_test = ds_test.rename_column("input", "text")

    all_labels = set()
    for split in [ds_train, ds_val, ds_test]:
        for example in split:
            all_labels.add(example["labels"])

    label_to_id = {label: idx for idx, label in enumerate(sorted(all_labels))}
    id_to_label = {idx: label for label, idx in label_to_id.items()}

    def convert_labels_to_ids(examples):
        examples["labels"] = [label_to_id[label] for label in examples["labels"]]
        return examples

    ds_train = ds_train.map(convert_labels_to_ids, batched=True)
    ds_val = ds_val.map(convert_labels_to_ids, batched=True)
    ds_test = ds_test.map(convert_labels_to_ids, batched=True)

    def tokenize_function(examples):
        tokenized = tokenizer(
            examples["text"], truncation=True, padding="max_length", max_length=128
        )
        return tokenized

    ds_train = ds_train.map(tokenize_function, batched=True)
    ds_val = ds_val.map(tokenize_function, batched=True)
    ds_test = ds_test.map(tokenize_function, batched=True)

    ds_train.set_format(
        type="torch",
        columns=["input_ids", "token_type_ids", "attention_mask", "labels"],
    )
    ds_val.set_format(
        type="torch",
        columns=["input_ids", "token_type_ids", "attention_mask", "labels"],
    )
    ds_test.set_format(
        type="torch",
        columns=["input_ids", "token_type_ids", "attention_mask", "labels"],
    )

    logger.info(f"ds_train: {ds_train[0]}")

    ds_train_shuffle = ds_train.shuffle(seed=42)

    def compute_metrics(eval_pred):
        predictions, labels = eval_pred
        predictions = np.argmax(predictions, axis=1)
        return {
            "balanced_accuracy": balanced_accuracy_score(predictions, labels),
            "accuracy": accuracy_score(predictions, labels),
        }

    args = TrainingArguments(
        output_dir="temp/",
        eval_strategy="epoch",
        save_strategy="epoch",
        logging_strategy="steps",
        logging_steps=50,
        learning_rate=2e-6,
        per_device_train_batch_size=32,
        per_device_eval_batch_size=32,
        num_train_epochs=3,
        weight_decay=0.1,
        load_best_model_at_end=True,
        metric_for_best_model="balanced_accuracy",
    )

    model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        num_labels=len(label_to_id),
        id2label=id_to_label,
        label2id=label_to_id,
    )

    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=ds_train_shuffle,
        eval_dataset=ds_val,
        compute_metrics=compute_metrics,
    )

    trainer.train()

    predictions = trainer.predict(ds_test)

    logger.info(f"Raw logits/predictions from the model: {predictions[0]}")
    logger.info(f"Labels from the dataset: {predictions[1]}")

    logger.info("Sentiment analysis completed")
