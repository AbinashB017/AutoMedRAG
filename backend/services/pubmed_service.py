import requests
import xml.etree.ElementTree as ET


def fetch_pubmed(query: str, max_results: int = 20):
    """
    Fetch papers from PubMed API based on a search query.
    Works for ALL medical domains — no hardcoded mock data.
    Returns an empty list if the query yields no results or the API fails.
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

        search_res = requests.get(search_url, params=search_params, timeout=15).json()
        id_list = search_res.get("esearchresult", {}).get("idlist", [])

        if not id_list:
            print(f"PubMed: no results for query '{query}'")
            return []

        fetch_params = {
            "db": "pubmed",
            "id": ",".join(id_list),
            "retmode": "xml"
        }

        fetch_res = requests.get(fetch_url, params=fetch_params, timeout=15)
        root = ET.fromstring(fetch_res.content)

        papers = []
        for article in root.findall(".//PubmedArticle"):
            try:
                title_elem = article.find(".//ArticleTitle")
                # Collect all AbstractText elements (structured abstracts have multiple)
                abstract_elems = article.findall(".//AbstractText")

                title = (title_elem.text or "").strip() if title_elem is not None else ""

                # Concatenate all abstract sections
                abstract_parts = []
                for elem in abstract_elems:
                    label = elem.get("Label", "")
                    text = (elem.text or "").strip()
                    if text:
                        if label:
                            abstract_parts.append(f"{label}: {text}")
                        else:
                            abstract_parts.append(text)
                abstract = " ".join(abstract_parts).strip()

                # Only include papers that have both a title and abstract
                if title and abstract:
                    papers.append({
                        "title": title,
                        "abstract": abstract
                    })
            except Exception as e:
                print(f"Error parsing article: {e}")
                continue

        if not papers:
            print(f"PubMed: fetched {len(id_list)} IDs but could not parse abstracts for '{query}'")

        return papers

    except requests.exceptions.Timeout:
        print(f"PubMed API timed out for query: '{query}'")
        return []
    except Exception as e:
        print(f"PubMed API error for query '{query}': {e}")
        return []
