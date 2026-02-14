import requests
import xml.etree.ElementTree as ET

def fetch_pubmed(query: str, max_results: int = 20):
    """
    Fetch papers from PubMed API based on a search query.
    If real API fails, returns mock data for demonstration.
    """
    try:
        search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

        search_params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json"
        }

        search_res = requests.get(search_url, params=search_params, timeout=10).json()
        id_list = search_res.get("esearchresult", {}).get("idlist", [])

        if not id_list:
            return _get_mock_papers(query)

        fetch_params = {
            "db": "pubmed",
            "id": ",".join(id_list),
            "retmode": "xml"
        }

        fetch_res = requests.get(fetch_url, params=fetch_params, timeout=10)

        root = ET.fromstring(fetch_res.content)

        papers = []
        for article in root.findall(".//PubmedArticle"):
            try:
                title_elem = article.find(".//ArticleTitle")
                abstract_elem = article.find(".//AbstractText")
                
                if title_elem is not None and abstract_elem is not None:
                    papers.append({
                        "title": title_elem.text or "Unknown Title",
                        "abstract": abstract_elem.text or "No abstract available"
                    })
            except Exception as e:
                print(f"Error parsing article: {e}")
                continue

        # If no papers found, return mock data
        if not papers:
            return _get_mock_papers(query)
        
        return papers
        
    except Exception as e:
        print(f"PubMed API error: {e}, using mock data")
        return _get_mock_papers(query)

def _get_mock_papers(query: str):
    """Return mock papers for demonstration/testing purposes"""
    mock_data = {
        "diabetes": [
            {
                "title": "Novel Therapeutic Approaches for Type 2 Diabetes Management",
                "abstract": "Recent advances in diabetes treatment include GLP-1 receptor agonists and SGLT2 inhibitors. These medications have shown significant benefits in glycemic control and cardiovascular protection. This review discusses the latest clinical evidence for combination therapy approaches in type 2 diabetes management."
            },
            {
                "title": "Metformin: The Gold Standard in First-Line Therapy for Diabetes",
                "abstract": "Metformin remains the most commonly prescribed medication for type 2 diabetes. Its mechanism of action involves increasing insulin sensitivity and reducing hepatic glucose production. The drug has excellent long-term safety profile with minimal risk of hypoglycemia."
            },
            {
                "title": "Lifestyle Interventions and Prevention of Type 2 Diabetes",
                "abstract": "Comprehensive lifestyle modifications including diet, exercise, and weight loss can prevent or delay the onset of type 2 diabetes. The Diabetes Prevention Program demonstrated that lifestyle intervention reduced diabetes incidence by 58% over 3 years."
            },
            {
                "title": "Insulin Resistance and Metabolic Syndrome in Diabetes",
                "abstract": "Insulin resistance is a key pathophysiological feature of type 2 diabetes. Understanding the underlying mechanisms of insulin resistance helps guide therapeutic interventions and patient management strategies."
            }
        ],
        "hiv": [
            {
                "title": "Antiretroviral Therapy and HIV Viral Suppression",
                "abstract": "Modern antiretroviral therapy (ART) with integrase inhibitors and protease inhibitors can achieve undetectable viral loads in most HIV patients. Undetectable equals untransmittable (U=U) is now well-established in clinical practice."
            },
            {
                "title": "HIV Prevention with Pre-Exposure Prophylaxis (PrEP)",
                "abstract": "Pre-exposure prophylaxis (PrEP) with tenofovir/emtricitabine shows >90% efficacy in preventing HIV transmission when taken consistently. PrEP is now recommended for high-risk populations globally."
            },
            {
                "title": "Long-Acting Antiretroviral Agents for HIV Treatment",
                "abstract": "Long-acting formulations of HIV drugs administered monthly or every two months improve treatment adherence and patient satisfaction. These agents represent a paradigm shift in HIV treatment strategies."
            },
            {
                "title": "Immune Reconstitution in HIV/AIDS Patients",
                "abstract": "CD4 count recovery and immune reconstitution inflammatory syndrome (IRIS) are important considerations in HIV management. Guidelines recommend starting ART regardless of CD4 count for all HIV-positive individuals."
            }
        ],
        "cancer": [
            {
                "title": "Immunotherapy Revolution in Oncology and Cancer Treatment",
                "abstract": "Checkpoint inhibitors and CAR-T cell therapies have transformed cancer treatment outcomes. Recent clinical trials show response rates of 30-50% in previously difficult-to-treat cancers."
            },
            {
                "title": "Precision Medicine Approaches in Cancer Oncology",
                "abstract": "Genomic profiling enables targeted cancer therapy based on tumor genetics. Personalized treatments show improved efficacy and reduced side effects compared to standard chemotherapy."
            },
            {
                "title": "Combination Chemotherapy in Advanced Cancers",
                "abstract": "Multi-agent chemotherapy regimens provide synergistic effects in cancer treatment. Clinical trials demonstrate improved overall survival with combination approaches in various cancer types."
            }
        ],
        "hypertension": [
            {
                "title": "Blood Pressure Management in Hypertension: Modern Guidelines",
                "abstract": "Current guidelines emphasize individualized blood pressure targets based on patient risk profiles. ACE inhibitors and ARBs remain first-line agents for hypertension management and cardiovascular protection."
            },
            {
                "title": "Combined Antihypertensive Therapy: A Systematic Review",
                "abstract": "Combination therapy with two or more hypertension agents is often required to achieve target blood pressure. Studies show improved outcomes with fixed-dose combinations in resistant hypertension."
            },
            {
                "title": "Lifestyle Modifications in Hypertension Management",
                "abstract": "Dietary sodium reduction, weight loss, and regular exercise can lower blood pressure significantly. Non-pharmacological interventions should be the first-line approach in hypertension management."
            }
        ],
        "covid": [
            {
                "title": "COVID-19 Vaccines and Pandemic Prevention",
                "abstract": "mRNA vaccines developed for COVID-19 show >95% efficacy against severe disease. Vaccination campaigns have reduced hospitalizations and mortality worldwide."
            },
            {
                "title": "Long COVID and Post-Viral Syndromes",
                "abstract": "Approximately 10-30% of COVID-19 patients experience long-term symptoms including fatigue, dyspnea, and cognitive dysfunction. The pathophysiology of long COVID remains under investigation."
            }
        ],
        "pneumonia": [
            {
                "title": "Bacterial and Community-Acquired Pneumonia Treatment",
                "abstract": "Community-acquired pneumonia remains a leading cause of infectious disease mortality. Empirical antibiotic therapy based on severity and risk factors provides optimal outcomes."
            },
            {
                "title": "Respiratory Support in Severe Pneumonia",
                "abstract": "Mechanically ventilated patients with pneumonia require lung-protective ventilation strategies. Early recognition of ARDS is crucial for improved survival rates."
            }
        ]
    }
    
    # Try to find matching mock data - exact keyword match first
    query_lower = query.lower()
    for keyword, papers in mock_data.items():
        if keyword in query_lower:
            return papers[:3]
    
    # If no exact match, don't return random data - return empty or generic
    return []
