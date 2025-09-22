import json
import os
import re

SCRAPER_PATH = os.path.dirname(os.path.abspath(__file__))
output_file = os.path.join(SCRAPER_PATH,'..','..','data','raw','lighthouses_uscg.txt')
with open(output_file, 'r', encoding='utf-8') as f:
    paragraphs = f.readlines()
    # This is nasty, but I'm hardcoding it...
    # remove the first 2 lines
    cleaned_paragraphs = paragraphs[2:]
    # remove all lines with \d\d\d: \[A-Z]
    cleaned_paragraphs = [p for p in cleaned_paragraphs if not re.match(r"^\d{3}: \[A-Z]", p)]
    # remove all ###:
    cleaned_paragraphs = [p.split(': ')[1] if ': ' in p else p for p in cleaned_paragraphs]
    # remove all \n
    cleaned_paragraphs = [p.strip() for p in cleaned_paragraphs if p.strip()]
    # Don't cross newlines when searching for a ')'
    pattern = re.compile(r"\((?![^\n)]*\))")

    joined = "\n".join(cleaned_paragraphs)
    fixed   = pattern.sub("(empty)", joined)
    cleaned_paragraphs = fixed.split("\n")
    fixed = ' '.join(cleaned_paragraphs)
    ugly = fixed.split(')')[:-1]
    lighthouses = [{'name': u.split(' (')[0].strip(), 'location': u.split(' (')[1].strip()} for u in ugly]
    print(lighthouses)
    with open(os.path.join(SCRAPER_PATH,'..','..','data','processed','lighthouses_uscg.json'), 'w', encoding='utf-8') as jf:
        json.dump(lighthouses, jf, indent=2)