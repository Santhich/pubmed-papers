import argparse
import csv
from pubmed_fetcher.client import fetch_pubmed_ids, fetch_paper_details
from pubmed_fetcher.models import Paper

def save_to_csv(papers: list[Paper], filename: str) -> None:
    """Save papers to CSV."""
    with open(filename, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            "PubmedID", "Title", "Publication Date",
            "Non-academic Author(s)", "Company Affiliation(s)", "Corresponding Author Email"
        ])
        for paper in papers:
            writer.writerow([
                paper.pubmed_id,
                paper.title,
                paper.publication_date,
                "; ".join(paper.non_academic_authors),
                "; ".join(paper.company_affiliations),
                paper.corresponding_author_email or ""
            ])

def main():
    parser = argparse.ArgumentParser(
        description="Fetch PubMed papers with authors from pharma/biotech companies."
    )
    parser.add_argument("query", help="PubMed query string")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug output")
    parser.add_argument("-f", "--file", help="Filename to save results as CSV")

    args = parser.parse_args()
    ids = fetch_pubmed_ids(args.query, debug=args.debug)
    papers = fetch_paper_details(ids, debug=args.debug)

    if args.file:
        save_to_csv(papers, args.file)
        print(f"Results saved to {args.file}")
    else:
        for paper in papers:
            print(paper)

if __name__ == "__main__":
    main()
