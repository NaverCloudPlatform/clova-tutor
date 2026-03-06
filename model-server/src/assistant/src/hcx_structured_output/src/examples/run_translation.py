# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

# examples/run_translation.py
import time

from src.tasks.translation import run_bilingual_segments

"""
This example uses text from the paper:

Attention Is All You Need
Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N. Gomez, Lukasz Kaiser, Illia Polosukhin
NeurIPS 2017

ArXiv: https://arxiv.org/abs/1706.03762

The FULL_TEXT variable contains the abstract of the above paper.
"""


FULL_TEXT = (
    """
    The dominant sequence transduction models are based on complex recurrent or convolutional neural networks in an encoder-decoder configuration.
    The best performing models also connect the encoder and decoder through an attention mechanism.
    We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely.
    Experiments on two machine translation tasks show these models to be superior in quality while being more parallelizable and requiring significantly less time to train.
    Our model achieves 28.4 BLEU on the WMT 2014 English-to-German translation task, improving over the existing best results, including ensembles by over 2 BLEU.
    On the WMT 2014 English-to-French translation task, our model establishes a new single-model state-of-the-art BLEU score of 41.8 after training for 3.5 days on eight GPUs, a small fraction of the training costs of the best models from the literature.
    We show that the Transformer generalizes well to other tasks by applying it successfully to English constituency parsing both with large and limited training data.
    """
).strip()

if __name__ == "__main__":
    start = time.time()
    final = run_bilingual_segments(FULL_TEXT)
    print("✅ Done", f"{time.time()-start:.2f}s")
    print(f"Total segments: {len(final.segments)}")
    print(final.model_dump())
