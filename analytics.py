import json
import re
from collections import Counter, defaultdict
from urllib.parse import urlparse, urldefrag

REPORT_FILE = "crawl_report_data.json"

STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "if", "while", "is", "are", "was",
    "were", "be", "been", "being", "to", "of", "in", "on", "for", "with",
    "as", "by", "at", "from", "this", "that", "these", "those", "it", "its",
    "you", "your", "we", "our", "they", "their", "he", "she", "his", "her",
    "them", "i", "me", "my", "mine", "not", "no", "yes", "do", "does", "did",
    "can", "could", "should", "would", "will", "just", "about", "into", "than",
    "then", "there", "here", "also", "all", "any", "more", "most", "other",
    "some", "such", "only", "own", "same", "so", "too", "very"
}

visited_urls = set()
word_counter = Counter()
subdomain_counter = defaultdict(int)
longest_url = ""
longest_word_count = 0


def collect_stats(url, soup):
    global longest_url, longest_word_count

    clean_url = urldefrag(url).url

    if clean_url in visited_urls:
        return

    visited_urls.add(clean_url)

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text(" ")
    words = re.findall(r"[a-zA-Z]+", text.lower())

    word_count = len(words)

    if word_count > longest_word_count:
        longest_word_count = word_count
        longest_url = clean_url

    filtered_words = [
        word for word in words
        if word not in STOP_WORDS and len(word) > 1
    ]

    word_counter.update(filtered_words)

    hostname = urlparse(clean_url).hostname

    if hostname and hostname.endswith("ics.uci.edu"):
        subdomain_counter[hostname] += 1

    save_report()


def save_report():
    data = {
        "unique_pages": len(visited_urls),
        "longest_page": {
            "url": longest_url,
            "word_count": longest_word_count
        },
        "top_50_words": word_counter.most_common(50),
        "subdomains": dict(sorted(subdomain_counter.items()))
    }

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    
    write_report_txt()


def write_report_txt():
    with open("report.txt", "w", encoding="utf-8") as f:

        f.write(f"Number of unique pages found: {len(visited_urls)}\n\n")

        f.write("Longest page found:\n")
        f.write(f"URL: {longest_url}\n")
        f.write(f"Word count: {longest_word_count}\n\n")

        f.write("50 most common words:\n")
        for word, count in word_counter.most_common(50):
            f.write(f"{word}: {count}\n")

        f.write("\nSubdomains found:\n")
        for subdomain, count in sorted(subdomain_counter.items()):
            f.write(f"{subdomain}, {count}\n")