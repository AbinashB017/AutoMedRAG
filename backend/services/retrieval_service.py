import numpy as np
import re
from collections import Counter

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

# Medical keyword synonyms for better matching
MEDICAL_SYNONYMS = {
    'pneumonia': ['pulmonary', 'lung', 'respiratory', 'bronc', 'chest'],
    'diabetes': ['glucose', 'insulin', 'blood sugar', 'metabolic'],
    'cancer': ['tumor', 'malignancy', 'oncology', 'carcinoma'],
    'heart': ['cardiac', 'cardiovascular', 'myocardial', 'coronary'],
    'infection': ['bacterial', 'viral', 'sepsis', 'inflammatory'],
}

def _clean_text(text):
    """Clean and normalize text"""
    if not text:
        return []
    text = text.lower()
    # Remove special characters
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    # Split into words and filter short words
    words = [w for w in text.split() if len(w) > 2]
    return words

def _calculate_relevance_score(query_words, title_words, abstract_words):
    """
    Calculate relevance score with title weighting and synonym matching.
    Higher weight for title matches, lower for abstract.
    """
    score = 0.0
    
    # Title matching (weight: 2.0)
    title_matches = len(set(query_words) & set(title_words))
    score += title_matches * 2.0
    
    # Abstract matching (weight: 1.0)
    abstract_matches = len(set(query_words) & set(abstract_words))
    score += abstract_matches * 1.0
    
    # Synonym matching (weight: 0.5)
    for query_word in query_words:
        if query_word in MEDICAL_SYNONYMS:
            synonyms = MEDICAL_SYNONYMS[query_word]
            synonym_matches = len(set(synonyms) & set(title_words + abstract_words))
            score += synonym_matches * 0.5
    
    # Normalize by query length
    if len(query_words) > 0:
        score = score / len(query_words)
    
    return score

def hybrid_retrieve(query, papers, top_k=10):
    """
    Perform hybrid retrieval using semantic and keyword search.
    Falls back to improved keyword matching if ML packages are not available.
    """
    
    if not papers:
        return []
    
    abstracts = [p.get("abstract", "") for p in papers]
    titles = [p.get("title", "") for p in papers]
    
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
    
    # Improved fallback: Smart keyword-based retrieval
    query_words = _clean_text(query)
    
    if not query_words:
        # If query is empty, return all papers
        ranked_papers = []
        for i, paper in enumerate(papers[:top_k]):
            paper_copy = paper.copy()
            paper_copy["hybrid_score"] = 0.1
            ranked_papers.append(paper_copy)
        return ranked_papers
    
    scores = []
    
    for abstract, title in zip(abstracts, titles):
        abstract_words = _clean_text(abstract)
        title_words = _clean_text(title)
        
        # Calculate relevance with improved scoring
        score = _calculate_relevance_score(query_words, title_words, abstract_words)
        scores.append(score)
    
    scores = np.array(scores)
    
    # Filter by minimum relevance threshold
    min_threshold = np.max(scores) * 0.1  # At least 10% of max score
    
    # Get indices of papers above threshold, sorted by score
    ranked_indices = np.argsort(scores)[::-1]
    
    ranked_papers = []
    for i in ranked_indices[:top_k]:
        if scores[i] >= min_threshold or len(ranked_papers) == 0:
            paper = papers[int(i)].copy()
            paper["hybrid_score"] = float(scores[int(i)])
            ranked_papers.append(paper)
    
    return ranked_papers
