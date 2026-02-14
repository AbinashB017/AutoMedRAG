import re
from collections import Counter

# Try to import ML packages with fallback
try:
    import numpy as np
    import faiss
    from rank_bm25 import BM25Okapi
    HAS_ML_PACKAGES = True
except ImportError:
    HAS_ML_PACKAGES = False
    np = None

try:
    from sentence_transformers import SentenceTransformer
    embed_model = SentenceTransformer("all-MiniLM-L6-v2")
    HAS_EMBEDDINGS = True
except ImportError:
    HAS_EMBEDDINGS = False
    embed_model = None

# Medical keyword synonyms for better matching
MEDICAL_SYNONYMS = {
    'pneumonia': ['pulmonary', 'lung', 'respiratory', 'bronc', 'chest', 'pneumon', 'alveol'],
    'diabetes': ['glucose', 'insulin', 'blood', 'sugar', 'metabolic', 'diabetic', 'hyperglycemia', 'hyperglycemic'],
    'cancer': ['tumor', 'malignancy', 'oncology', 'carcinoma', 'cancer', 'neoplasm', 'metasta'],
    'hiv': ['hiv', 'aids', 'immunodeficiency', 'antiretroviral', 'arv', 'retroviral', 'cd4'],
    'heart': ['cardiac', 'cardiovascular', 'myocardial', 'coronary', 'heart', 'cardiov', 'arrhythm'],
    'infection': ['bacterial', 'viral', 'sepsis', 'inflammatory', 'infection', 'infect', 'pathog'],
    'covid': ['covid', 'coronavirus', 'sars-cov', 'pandemic', 'respiratory', 'sars'],
    'hypertension': ['hypertension', 'blood', 'pressure', 'bp', 'hypertensive', 'systolic'],
    'arthritis': ['arthritis', 'joint', 'rheumatoid', 'osteoarthritis', 'arthr', 'inflammation'],
    'spondylitis': ['spondylitis', 'spine', 'vertebra', 'ankylosing', 'spinal', 'backbone', 'spondylo'],
    'asthma': ['asthma', 'bronchial', 'wheeze', 'wheez', 'airway', 'obstruct'],
    'kidney': ['kidney', 'renal', 'nephr', 'glomerulonephritis', 'creatinine', 'dialysis'],
    'liver': ['liver', 'hepatic', 'hepatitis', 'cirrhosis', 'fibrosis', 'portal'],
    'thyroid': ['thyroid', 'hyperthyroidism', 'hypothyroidism', 'thyroiditis', 'tsh'],
    'depression': ['depression', 'depressive', 'mood', 'psychiatric', 'antidepressant', 'ssri'],
    'alzheimer': ['alzheimer', 'dementia', 'cognitive', 'neurodegenerative', 'tau', 'amyloid'],
    'migraine': ['migraine', 'headache', 'neurological', 'tension', 'cluster'],
    'stroke': ['stroke', 'cerebral', 'ischemic', 'thrombotic', 'hemorrhagic', 'tia'],
    'obesity': ['obesity', 'overweight', 'weight', 'metabolic', 'bmi', 'adiposity'],
    'gout': ['gout', 'uric', 'purine', 'arthralgia', 'acute'],
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
    STRICT: Requires keyword presence in title or abstract.
    """
    score = 0.0
    
    # Check if ANY query word is in title (strict requirement)
    has_title_match = len(set(query_words) & set(title_words)) > 0
    has_abstract_match = len(set(query_words) & set(abstract_words)) > 0
    
    if not has_title_match and not has_abstract_match:
        # Check if any synonyms of query words are in title/abstract
        has_synonym_match = False
        for query_word in query_words:
            if query_word in MEDICAL_SYNONYMS:
                synonyms = MEDICAL_SYNONYMS[query_word]
                if len(set(synonyms) & set(title_words + abstract_words)) > 0:
                    has_synonym_match = True
                    break
        if not has_synonym_match:
            return 0.0  # REJECT: No keyword or synonym at all
    
    # Title matching (weight: 4.0) - strongest signal
    title_matches = len(set(query_words) & set(title_words))
    score += title_matches * 4.0
    
    # Abstract matching (weight: 1.5)
    abstract_matches = len(set(query_words) & set(abstract_words))
    score += abstract_matches * 1.5
    
    # Synonym matching (weight: 2.0)
    for query_word in query_words:
        if query_word in MEDICAL_SYNONYMS:
            synonyms = MEDICAL_SYNONYMS[query_word]
            synonym_matches = len(set(synonyms) & set(title_words + abstract_words))
            score += synonym_matches * 2.0
    
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

            dimension = len(doc_embeddings[0]) if doc_embeddings else 768
            index = faiss.IndexFlatL2(dimension)
            
            # Convert to numpy arrays for FAISS
            doc_array = np.array(doc_embeddings, dtype=np.float32)
            query_array = np.array([query_embedding[0]], dtype=np.float32)
            
            index.add(doc_array)

            D, I = index.search(query_array, len(abstracts))
            dense_scores = 1 / (1 + D[0])

            tokenized = [doc.split() for doc in abstracts]
            bm25 = BM25Okapi(tokenized)
            bm25_scores = bm25.get_scores(query.split())
            bm25_scores = np.array(bm25_scores, dtype=np.float32)

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
    
    # Filter by minimum relevance threshold using pure Python
    max_score = max(scores) if scores else 0
    min_threshold = max(max_score * 0.4, 1.0)  # At least 40% of max OR 1.0 (whichever is higher) - STRICT
    
    # Get indices of papers above threshold, sorted by score (pure Python)
    scored_with_index = [(score, i) for i, score in enumerate(scores)]
    scored_with_index.sort(reverse=True)
    ranked_indices = [i for score, i in scored_with_index if score >= min_threshold]
    
    # Ensure we have results - if threshold is too strict, relax it slightly
    if len(ranked_indices) == 0:
        # Only relax if we have some results to show
        min_threshold_relaxed = max(max_score * 0.2, 0.5)  # 20% or 0.5
        ranked_indices = [i for score, i in scored_with_index if score >= min_threshold_relaxed]
    
    if len(ranked_indices) == 0:
        ranked_indices = [i for score, i in scored_with_index][:top_k]
    
    ranked_papers = []
    for i in ranked_indices[:top_k]:
        paper = papers[int(i)].copy()
        paper["hybrid_score"] = float(scores[i])
        ranked_papers.append(paper)
    
    return ranked_papers
