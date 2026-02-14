import numpy as np

# Try to import ML packages with fallback
try:
    from sentence_transformers import CrossEncoder
    cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    HAS_CROSS_ENCODER = True
except ImportError:
    HAS_CROSS_ENCODER = False
    cross_encoder = None

def rerank(query, papers, top_k=3):
    """
    Re-rank papers by relevance using cross-encoder.
    Falls back to using hybrid_score if cross-encoder is not available.
    """
    
    if not papers or len(papers) == 0:
        return []
    
    # Try with cross-encoder if available
    if HAS_CROSS_ENCODER:
        try:
            pairs = [[query, p.get("abstract", "")] for p in papers]
            scores = cross_encoder.predict(pairs)
            
            ranked = sorted(zip(papers, scores), key=lambda x: x[1], reverse=True)
            
            top_papers = []
            for paper, score in ranked[:top_k]:
                paper_copy = paper.copy()
                paper_copy["rerank_score"] = float(score)
                top_papers.append(paper_copy)
            
            return top_papers
        except Exception as e:
            print(f"Cross-encoder failed, using hybrid scores: {e}")
    
    # Fallback: Use existing hybrid_score or default
    papers_copy = [p.copy() for p in papers]
    
    # Sort by hybrid_score if it exists, otherwise use position
    for i, paper in enumerate(papers_copy):
        if "rerank_score" not in paper:
            # Use hybrid_score if available, otherwise assign based on position
            if "hybrid_score" in paper:
                paper["rerank_score"] = paper["hybrid_score"]
            else:
                paper["rerank_score"] = 1.0 / (i + 1)  # Inverse position score
    
    # Sort and return top_k
    ranked = sorted(papers_copy, key=lambda x: x.get("rerank_score", 0), reverse=True)
    return ranked[:top_k]
