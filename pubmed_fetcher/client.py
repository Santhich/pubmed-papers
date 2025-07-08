import requests
from typing import List
from .models import Paper
from xml.etree import ElementTree as ET

BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

def fetch_pubmed_ids(query: str, debug: bool = False) -> List[str]:
    """Fetch PubMed IDs matching the query."""
    params = {
        "db": "pubmed",
        "term": query,
        "retmax": 100
    }
    response = requests.get(f"{BASE_URL}/esearch.fcgi", params=params)
    response.raise_for_status()
    ids = ET.fromstring(response.text).findall(".//Id")
    if debug:
        print(f"Fetched IDs: {[id.text for id in ids]}")
    return [id.text for id in ids]

def fetch_paper_details(pubmed_ids: List[str], debug: bool = False) -> List[Paper]:
    """Fetch detailed paper data for given PubMed IDs."""
    papers: List[Paper] = []
    if not pubmed_ids:
        return papers

    ids_str = ",".join(pubmed_ids)
    params = {
        "db": "pubmed",
        "id": ids_str,
        "retmode": "xml"
    }
    response = requests.get(f"{BASE_URL}/efetch.fcgi", params=params)
    response.raise_for_status()
    root = ET.fromstring(response.text)
    articles = root.findall(".//PubmedArticle")

    for article in articles:
        pmid = article.findtext(".//PMID")
        title = article.findtext(".//ArticleTitle", default="")
        pub_date_elem = article.find(".//PubDate")
        if pub_date_elem is not None:
            year = pub_date_elem.findtext("Year") or "Unknown"
        else:
            year = "Unknown"

        # Extract authors
        non_academic_authors = []
        company_affiliations = []
        corresponding_email = None

        for author in article.findall(".//Author"):
            last_name = author.findtext("LastName", default="")
            fore_name = author.findtext("ForeName", default="")
            affiliation = author.findtext(".//Affiliation", default="")

            if not affiliation:
                continue

            # Heuristic: Identify non-academic authors
            from .filters import is_non_academic
            if is_non_academic(affiliation):
                author_name = f"{fore_name} {last_name}".strip()
                non_academic_authors.append(author_name)
                company_affiliations.append(affiliation)

            # Extract email if present
            if "@" in affiliation and corresponding_email is None:
                corresponding_email = extract_email(affiliation)

        paper = Paper(
            pubmed_id=pmid,
            title=title,
            publication_date=year,
            non_academic_authors=non_academic_authors,
            company_affiliations=company_affiliations,
            corresponding_author_email=corresponding_email
        )
        if debug:
            print(f"Paper: {paper}")
        papers.append(paper)

    return papers

from .utils import extract_email
