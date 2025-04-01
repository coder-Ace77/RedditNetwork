import requests
import csv
from bs4 import BeautifulSoup

def scrape_reddit_best(n_pages=5):
    base_url = "https://www.reddit.com/best/communities/"
    headers = {"User-Agent": "Mozilla/5.0"}  # Mimic a browser request
    
    data = []
    
    for page in range(1, n_pages + 1):
        url = f"{base_url}{page}"
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            print(f"Failed to fetch page {page}")
            continue
        
        soup = BeautifulSoup(response.text, "html.parser")
        communities = soup.find_all("div", attrs={"data-prefixed-name": True, "data-subscribers-count": True})
        
        for rank, community in enumerate(communities, start=1 + (page - 1) * len(communities)):
            subreddit = community["data-prefixed-name"]
            subreddit = subreddit[2:]
            subscribers = community["data-subscribers-count"]
            data.append([rank, subreddit, subscribers])
    
    # Save to CSV
    with open("output/reddit_best_communities_complete.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Rank", "Subreddit", "Subscribers"])
        writer.writerows(data)

    print("Scraping complete. Data saved to 'reddit_best_communities.csv'.")

# Run for first 5 pages
scrape_reddit_best(n_pages=100)
