import numpy as np

# Try to import ML packages with fallback
try:
    import faiss
    from rank_bm25 import BM25Okapi
    HAS_ML_PACKAGES = True
except ImportError:
    HAS_ML_PACKAGES = False

try:
    from sentence_transformers import SentenceTransformer
    embed_model = SentenceTransformer("all-MiniLM-L6-v2")
    HAS_EMBEDDINGS = True
except ImportError:
    HAS_EMBEDDINGS = False
    embed_model = None

def hybrid_retrieve(query, papers, top_k=10):
    """
    Perform hybrid retrieval using semantic and keyword search.
    Falls back to simple keyword matching if ML packages are not available.
    """
    
    if not papers:
        return []
    
    abstracts = [p.get("abstract", "") for p in papers]
    
    # Try hybrid retrieval with ML packages
    if HAS_ML_PACKAGES and HAS_EMBEDDINGS:
        try:
            doc_embeddings = embed_model.encode(abstracts)
            query_embedding = embed_model.encode([query])

            dimension = doc_embeddings.shape[1]
            index = faiss.IndexFlatL2(dimension)
            index.add(np.array(doc_embeddings))

            D, I = index.search(np.array(query_embedding), len(abstracts))
            dense_scores = 1 / (1 + D[0])

            tokenized = [doc.split() for doc in abstracts]
            bm25 = BM25Okapi(tokenized)
            bm25_scores = bm25.get_scores(query.split())

            dense_scores = dense_scores / (np.max(dense_scores) + 1e-8)
            bm25_scores = bm25_scores / (np.max(bm25_scores) + 1e-8)

            final_scores = 0.5 * dense_scores + 0.5 * bm25_scores
            ranked_indices = np.argsort(final_scores)[::-1][:top_k]

            ranked_papers = []
            for i in ranked_indices:
                paper = papers[int(i)].copy()
                paper["hybrid_score"] = float(final_scores[int(i)])
                ranked_papers.append(paper)

            return ranked_papers
        except Exception as e:
            print(f"ML retrieval failed, falling back to keyword search: {e}")
    
    # Fallback: Simple keyword-based retrieval
    query_terms = set(query.lower().split())
    scores = []
    
    for abstract in abstracts:
        abstract_terms = set(abstract.lower().split())
        # Calculate Jaccard similarity
        if len(abstract_terms.union(query_terms)) == 0:
            score = 0
        else:
            intersection = len(query_terms.intersection(abstract_terms))
            union = len(query_terms.union(abstract_terms))
            score = intersection / union
        scores.append(score)
    
    scores = np.array(scores)
    ranked_indices = np.argsort(scores)[::-1][:top_k]
    
    ranked_papers = []
    for i in ranked_indices:
        if scores[i] > 0:  # Only include papers with some relevance
            paper = papers[int(i)].copy()
            paper["hybrid_score"] = float(scores[int(i)])
            ranked_papers.append(paper)
    
    return ranked_papers
