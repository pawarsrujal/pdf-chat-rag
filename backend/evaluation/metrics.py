"""
Evaluation metrics for RAG system.
"""

from typing import List, Set
import time


def precision_at_k(retrieved_docs: List[str], relevant_docs: Set[str], k: int) -> float:
    """
    Calculate Precision@k.

    Args:
        retrieved_docs: List of retrieved document IDs.
        relevant_docs: Set of relevant document IDs.
        k: Number of top results to consider.

    Returns:
        Precision@k score.
    """
    if k == 0:
        return 0.0
    
    retrieved_at_k = retrieved_docs[:k]
    relevant_retrieved = len(set(retrieved_at_k) & relevant_docs)
    return relevant_retrieved / k if k > 0 else 0.0


def recall_at_k(retrieved_docs: List[str], relevant_docs: Set[str], k: int) -> float:
    """
    Calculate Recall@k.

    Args:
        retrieved_docs: List of retrieved document IDs.
        relevant_docs: Set of relevant document IDs.
        k: Number of top results to consider.

    Returns:
        Recall@k score.
    """
    if not relevant_docs:
        return 0.0
    
    retrieved_at_k = set(retrieved_docs[:k])
    relevant_retrieved = len(retrieved_at_k & relevant_docs)
    return relevant_retrieved / len(relevant_docs)


def mean_reciprocal_rank(retrieved_docs: List[str], relevant_docs: Set[str]) -> float:
    """
    Calculate Mean Reciprocal Rank (MRR).

    Args:
        retrieved_docs: List of retrieved document IDs in order.
        relevant_docs: Set of relevant document IDs.

    Returns:
        MRR score.
    """
    for i, doc_id in enumerate(retrieved_docs):
        if doc_id in relevant_docs:
            return 1.0 / (i + 1)
    return 0.0


def average_precision(retrieved_docs: List[str], relevant_docs: Set[str]) -> float:
    """
    Calculate Average Precision (AP).

    Args:
        retrieved_docs: List of retrieved document IDs in order.
        relevant_docs: Set of relevant document IDs.

    Returns:
        AP score.
    """
    if not relevant_docs:
        return 0.0
    
    relevant_found = 0
    precision_sum = 0.0
    
    for i, doc_id in enumerate(retrieved_docs):
        if doc_id in relevant_docs:
            relevant_found += 1
            precision_at_i = relevant_found / (i + 1)
            precision_sum += precision_at_i
    
    return precision_sum / len(relevant_docs) if relevant_docs else 0.0