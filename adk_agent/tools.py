import re
import requests


def stackoverflow_search_rss(query: str) -> dict:
    """
    Search Stack Overflow via RSS (stable fallback).
    Returns up to 3 results with title/link. If fails, returns popular tag links.
    """
    rss_url = f"https://stackoverflow.com/feeds?search={requests.utils.quote(query)}"
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; WebexBot/1.0)",
        "Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.8",
    }
    try:
        resp = requests.get(rss_url, headers=headers, timeout=8)
        resp.raise_for_status()
        text = resp.text
        items = re.findall(r"<entry>(.*?)</entry>", text, flags=re.DOTALL | re.IGNORECASE)
        results = []
        for raw in items:
            title_match = re.search(r"<title>(.*?)</title>", raw, flags=re.DOTALL | re.IGNORECASE)
            link_match = re.search(r"<link[^>]*href=\"(.*?)\"[^>]*/>", raw, flags=re.DOTALL | re.IGNORECASE)
            title = title_match.group(1).strip() if title_match else None
            link = link_match.group(1).strip() if link_match else None
            if title and link:
                results.append({"title": title, "link": link})
            if len(results) >= 3:
                break
        if results:
            return {"results": results, "source": "rss"}
    except Exception as e:
        rss_error = str(e)

    fallback_results = [
        {"title": "Stack Overflow - Questions tagged 'python'", "link": "https://stackoverflow.com/questions/tagged/python"},
        {"title": "Stack Overflow - Questions tagged 'javascript'", "link": "https://stackoverflow.com/questions/tagged/javascript"},
        {"title": "Stack Overflow - Questions tagged 'c++'", "link": "https://stackoverflow.com/questions/tagged/c%2b%2b"},
        {"title": "Stack Overflow - Questions tagged 'java'", "link": "https://stackoverflow.com/questions/tagged/java"},
    ]
    return {"results": fallback_results, "source": f"fallback: {rss_error if 'rss_error' in locals() else 'unknown error'}"}


INFOBAE_RSS_CANDIDATES = [
    "https://www.infobae.com/arc/outboundfeeds/rss/?outputType=xml",
    "https://www.infobae.com/rss",
    "https://www.infobae.com/feeds/rss/",
]


def infobae_headlines(topic: str | None = None, limit: int = 5) -> dict:
    """
    Fetch latest Infobae headlines (optionally filter by topic).
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; WebexBot/1.0)",
        "Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.8",
    }
    errors = []
    for url in INFOBAE_RSS_CANDIDATES:
        try:
            resp = requests.get(url, headers=headers, timeout=8)
            resp.raise_for_status()
            text = resp.text

            items = re.findall(r"<item>(.*?)</item>", text, flags=re.DOTALL | re.IGNORECASE)
            results = []
            for raw in items:
                title_match = re.search(r"<title><!\[CDATA\[(.*?)\]\]></title>|<title>(.*?)</title>", raw, flags=re.DOTALL | re.IGNORECASE)
                link_match = re.search(r"<link>(.*?)</link>", raw, flags=re.DOTALL | re.IGNORECASE)
                title = None
                if title_match:
                    title = title_match.group(1) or title_match.group(2)
                link = link_match.group(1).strip() if link_match else None
                if not title:
                    continue
                if topic and topic.lower() not in title.lower():
                    continue
                results.append({"title": title.strip(), "link": link})
                if len(results) >= limit:
                    break
            if results:
                return {"results": results, "source": url}
        except Exception as e:
            errors.append(f"{url}: {e}")
            continue
    if errors:
        return {"error": f"Infobae fetch failed. Tried: {errors}"}
    return {"message": "No Infobae headlines found for the given topic."}


def build_tools():
    """
    Build the default tool list. Add your own callables here.
    """
    return [stackoverflow_search_rss, infobae_headlines]

