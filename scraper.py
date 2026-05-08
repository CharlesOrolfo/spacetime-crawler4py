import re
import analytics
from urllib.parse import urlparse,urljoin, urldefrag
from bs4 import BeautifulSoup

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    
    links = []
    
    if resp.status != 200 or not resp.raw_response or not resp.raw_response.content:
        return links

    content_type = resp.raw_response.headers.get("Content-Type", "").lower()
    
    if "text/html" not in content_type:
        return links

    html = resp.raw_response.content

    soup = BeautifulSoup(html, "html.parser")
    
    # Data Collection
    analytics.collect_stats(resp.raw_response.url, soup)

    for tag in soup.find_all("a"):
        href = tag.get("href")

        if not href:
            continue

        try:
            absolute_url = urljoin(resp.raw_response.url, href)
            clean_url = urldefrag(absolute_url).url
        except ValueError:
            continue

        links.append(clean_url)

    return links

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        
        # Scheme Check
        if parsed.scheme not in set(["http", "https"]):
            return False

        # Hostname Check
        hostname = parsed.hostname
        if not hostname:
            return False

        hostname = hostname.lower()
        path = parsed.path.lower()
        query = parsed.query.lower()
        full_url = url.lower()

        valid_domains = [
            "ics.uci.edu",
            "cs.uci.edu",
            "informatics.uci.edu",
            "stat.uci.edu"
        ]
        
        bad_path_substrings = [
            "/site/login",
            "/users/sign_in",
            "/help",
            "/explore",
            "/releases/",
            "/release/",
            "/src/",
            "/raw-attachment/",
            "/attachment/",
            "_files/",
        ]

        bad_url_substrings = [
            "filter",
            "tribe__",
            "subpage",
            "%5b",
            "%5d",
            "do=",
            "idx=",
            "ical=",
            "people=",
            "export_",
            "login",
            "edit",
        ]
        
        bad_path_regexes = [
            r"/page/\d+", # Bad Path/Pagination Trap
            r"/\d{4}-\d{2}-\d{2}(/|$)", # Calendar/date traps
            r"/\d{4}/\d{2}(/|$)",
            r"/t?sld\d+\.htm?$", # Presentation traps
            r"(sld|tsld|slide)\d+\.htm?$",
            r"slide\d+\.htm?$",
        ]

        # Domain and Subdomain Check
        if not any(
            hostname == domain or hostname.endswith("." + domain)
            for domain in valid_domains
        ):
            return False

        if len(url) > 300:
            return False

        if query:
            return False

        if any(pattern in full_url for pattern in bad_url_substrings):
            return False

        if any(pattern in path for pattern in bad_path_substrings):
            return False

        if any(re.search(pattern, path) for pattern in bad_path_regexes):
            return False

        if "/presentations/" in path and path.endswith(".htm"):
            return False

        # Extension Check
        if re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz"
            + r"|py|cc|cpp|c|h|hpp|java|class|txt|md"
            + r"|sql|shtml)$",
            parsed.path.lower()
        ):
            return False
        
        return True

    except TypeError:
        print ("TypeError for ", parsed)
        raise
