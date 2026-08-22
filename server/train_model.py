"""
train_model.py — CLI entry point for training the PM2.5 model.

Usage: python train_model.py
Requires data from generate_data.py to exist in the database.
"""

from ml_model import train_model

if __name__ == "__main__":
    print("Training PM2.5 prediction model...\n")
    train_model()
    print("\nDone. The model is served automatically by /api/predict.")
