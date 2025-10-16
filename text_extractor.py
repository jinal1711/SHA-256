
import re
from typing import Tuple
import requests
from bs4 import BeautifulSoup

URL_MARK = "https://quod.lib.umich.edu/cgi/r/rsv/rsv-idx?type=DIV1&byte=4697892"

def fetch_html(url: str = URL_MARK, timeout: int = 30) -> str:
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()
    return r.text

def extract_visible_text(html: str) -> str:
    """
    Return the full visible text (naive): HTML tags removed, scripts/styles removed.
    This is the RAW extracted text.
    """
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text("\n")
    
    lines = [ln.rstrip() for ln in text.splitlines()]
   
    return "\n".join(lines).strip()

def clean_scripture_text(raw_text: str, remove_bracket_numbers: bool = True,
                         remove_colon_verse_nums: bool = True,
                         collapse_whitespace: bool = True) -> str:
    """
    Attempt to keep only the scripture text for the Book of Mark:
    - Remove village headings, navigation text and most bracketed notes heuristically
    - Remove verse numbers like [1], (1), or inline chapter:verse like '1:1' depending on flags
    - Collapse whitespace to single spaces
    Note: this is heuristic; inspect the result for your grader's expectations.
    """
    txt = raw_text

    
    lines = txt.splitlines()
    start_idx = 0
    for i, ln in enumerate(lines):
        if ln.strip().lower() == "mark":
            start_idx = i
            break
    txt = "\n".join(lines[start_idx:])

    
    txt = re.sub(r'(?m)^\s*(Return to|Contents|Index|Search|Table of Contents).*\n', '', txt)

    if remove_bracket_numbers:
        txt = re.sub(r'\[\s*\d+\s*\]', ' ', txt)   # [1]
        txt = re.sub(r'\(\s*\d+\s*\)', ' ', txt)   # (1)

    if remove_colon_verse_nums:
        # Remove chapter:verse patterns like "1:1" when they appear inline 
        txt = re.sub(r'\b\d{1,3}:\d{1,3}\b', ' ', txt)

    # Remove stray leading verse numbers at line starts like "1 " or "1." or "1)"
    txt = re.sub(r'(?m)^\s*\d+\s*[\.\)]?\s*', '', txt)

    # Remove multiple blank lines
    txt = re.sub(r'\n{2,}', '\n\n', txt)

    if collapse_whitespace:
        # collapse all whitespace to single space, but keep paragraph breaks 
        txt = txt.replace('\n\n', '<<PARA>>')
        txt = re.sub(r'\s+', ' ', txt)
        txt = txt.replace('<<PARA>>', '\n\n')
        txt = txt.strip()

    return txt
