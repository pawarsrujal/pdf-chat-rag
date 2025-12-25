"""
Example evaluation script for the RAG system.
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

from services.rag import RAGService
from services.embeddings import EmbeddingService
from services.retriever import RetrieverService
from services.llm import LLMService
from db.faiss_db import FAISSDatabase
from evaluation.evaluator import RAGEvaluator, EvaluationSample


def main():
    """Run example evaluation."""
    
    # Initialize services
    embedding_service = EmbeddingService()
    faiss_db = FAISSDatabase()
    retriever_service = RetrieverService(faiss_db)
    llm_service = LLMService(api_key=os.getenv("OPENAI_API_KEY", ""))
    rag_service = RAGService(embedding_service, retriever_service, llm_service)
    
    # Create evaluator
    evaluator = RAGEvaluator(rag_service)
    
    # Example evaluation samples
    # Note: In practice, these would be based on actual documents in the system
    samples = [
        EvaluationSample(
            query="What is machine learning?",
            relevant_docs={"machine_learning_basics.pdf", "ai_fundamentals.pdf"},
            role="student"
        ),
        EvaluationSample(
            query="How does RAG improve LLM responses?",
            relevant_docs={"rag_paper.pdf", "retrieval_augmented_generation.pdf"},
            role="researcher"
        ),
        EvaluationSample(
            query="Explain the difference between supervised and unsupervised learning.",
            relevant_docs={"machine_learning_basics.pdf"},
            role="interview"
        ),
        EvaluationSample(
            query="What are the main components of a neural network?",
            relevant_docs={"deep_learning_guide.pdf", "neural_networks.pdf"},
            role="student"
        ),
        EvaluationSample(
            query="How to optimize vector database performance?",
            relevant_docs={"vector_databases.pdf", "faiss_optimization.pdf"},
            role="researcher"
        )
    ]
    
    print("Running RAG evaluation...")
    print(f"Evaluating {len(samples)} samples...")
    
    # Evaluate dataset
    avg_metrics = evaluator.evaluate_dataset(samples, top_k=5, similarity_threshold=0.5)
    
    print("\nEvaluation Results:")
    print("=" * 50)
    for metric, value in avg_metrics.items():
        print(f"{metric}: {value}")
    
    # Export results
    output_path = "evaluation_results.csv"
    evaluator.export_to_csv(output_path)
    print(f"\nDetailed results exported to {output_path}")


if __name__ == "__main__":
    main()