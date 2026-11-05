"""
src/utils/determinism.py

Centralized determinism configuration for TensorFlow/Keras training.
Ensures reproducible training across fresh processes.
"""

import os
import random
import hashlib
import numpy as np


def enable_determinism(seed: int = 42):
    """
    Configures environment variables and TensorFlow settings for deterministic operation.
    Must be invoked before TensorFlow ops/models are initialized.
    """
    os.environ["TF_DETERMINISTIC_OPS"] = "1"
    os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
    os.environ["PYTHONHASHSEED"] = str(seed)

    random.seed(seed)
    np.random.seed(seed)

    import tensorflow as tf
    tf.keras.utils.set_random_seed(seed)
    tf.config.experimental.enable_op_determinism()


def compute_weights_hash(model) -> str:
    """
    Computes a deterministic SHA-256 hash over all model layer weights.
    """
    hasher = hashlib.sha256()
    for w in model.get_weights():
        hasher.update(w.tobytes())
    return hasher.hexdigest()

