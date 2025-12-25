"""
RAG Evaluator for measuring system performance.
"""

import csv
import time
import logging
from typing import List, Dict, Any, Set, Optional
from pathlib import Path
from services.rag import RAGService
from models.schemas import ChatRequest
from evaluation.metrics import precision_at_k, recall_at_k, mean_reciprocal_rank, average_precision

logger = logging.getLogger(__name__)


class EvaluationSample:
    """Represents a single evaluation sample."""
    
    def __init__(self, query: str, relevant_docs: Set[str], role: str = "researcher"):
        self.query = query
        self.relevant_docs = relevant_docs
        self.role = role


class RAGEvaluator:
    """Evaluator for RAG system performance."""
    
    def __init__(self, rag_service: RAGService):
        """
        Initialize the evaluator.
        
        Args:
            rag_service: Instance of RAGService to evaluate.
        """
        self.rag_service = rag_service
        self.results: List[Dict[str, Any]] = []
    
    def evaluate_sample(self, sample: EvaluationSample, top_k: int = 5, similarity_threshold: float = 0.5) -> Dict[str, Any]:
        """
        Evaluate a single sample.
        
        Args:
            sample: EvaluationSample to test.
            top_k: Number of top results to retrieve.
            similarity_threshold: Similarity threshold for retrieval.
            
        Returns:
            Dictionary with evaluation metrics.
        """
        # Create chat request
        request = ChatRequest(
            message=sample.query,
            top_k=top_k,
            similarity_threshold=similarity_threshold,
            role=sample.role
        )
        
        # Measure latency
        start_time = time.time()
        response = self.rag_service.process_query(request)
        end_to_end_latency = time.time() - start_time
        
        # Extract retrieved document IDs
        retrieved_docs = [source.document_name for source in response.sources]
        
        # Calculate metrics
        p_at_1 = precision_at_k(retrieved_docs, sample.relevant_docs, 1)
        p_at_3 = precision_at_k(retrieved_docs, sample.relevant_docs, 3)
        p_at_5 = precision_at_k(retrieved_docs, sample.relevant_docs, 5)
        
        r_at_1 = recall_at_k(retrieved_docs, sample.relevant_docs, 1)
        r_at_3 = recall_at_k(retrieved_docs, sample.relevant_docs, 3)
        r_at_5 = recall_at_k(retrieved_docs, sample.relevant_docs, 5)
        
        mrr = mean_reciprocal_rank(retrieved_docs, sample.relevant_docs)
        ap = average_precision(retrieved_docs, sample.relevant_docs)
        
        # Token usage (placeholder - would need to track from LLM service)
        token_usage = getattr(response, 'token_usage', 0)
        
        result = {
            "query": sample.query,
            "role": sample.role,
            "retrieved_docs": retrieved_docs,
            "relevant_docs": list(sample.relevant_docs),
            "response": response.response,
            "end_to_end_latency": round(end_to_end_latency, 3),
            "token_usage": token_usage,
            "precision@1": round(p_at_1, 3),
            "precision@3": round(p_at_3, 3),
            "precision@5": round(p_at_5, 3),
            "recall@1": round(r_at_1, 3),
            "recall@3": round(r_at_3, 3),
            "recall@5": round(r_at_5, 3),
            "mrr": round(mrr, 3),
            "map": round(ap, 3),
            "top_k": top_k,
            "similarity_threshold": similarity_threshold
        }
        
        self.results.append(result)
        logger.info(f"Evaluated query: {sample.query[:50]}... P@5: {p_at_1:.3f}, Latency: {end_to_end_latency:.3f}s")
        
        return result
    
    def evaluate_dataset(self, samples: List[EvaluationSample], top_k: int = 5, similarity_threshold: float = 0.5) -> Dict[str, float]:
        """
        Evaluate a dataset of samples.
        
        Args:
            samples: List of EvaluationSample instances.
            top_k: Number of top results to retrieve.
            similarity_threshold: Similarity threshold for retrieval.
            
        Returns:
            Dictionary with average metrics.
        """
        self.results = []
        
        for sample in samples:
            self.evaluate_sample(sample, top_k, similarity_threshold)
        
        # Calculate averages
        if not self.results:
            return {}
        
        avg_metrics = {}
        metric_keys = ["end_to_end_latency", "token_usage", "precision@1", "precision@3", "precision@5", 
                       "recall@1", "recall@3", "recall@5", "mrr", "map"]
        
        for key in metric_keys:
            values = [r[key] for r in self.results if key in r]
            avg_metrics[f"avg_{key}"] = round(sum(values) / len(values), 3) if values else 0.0
        
        logger.info(f"Dataset evaluation complete. Avg P@5: {avg_metrics.get('avg_precision@5', 0):.3f}")
        
        return avg_metrics
    
    def export_to_csv(self, filepath: str):
        """
        Export evaluation results to CSV.
        
        Args:
            filepath: Path to save the CSV file.
        """
        if not self.results:
            logger.warning("No results to export")
            return
        
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            if self.results:
                fieldnames = self.results[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.results)
        
        logger.info(f"Results exported to {filepath}")