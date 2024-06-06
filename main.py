import sys
import os
from bs4 import BeautifulSoup
import requests

url_root = "https://www.royalroad.com"
try:
    book_id = sys.argv[1]
except:
    print("Error: No book id provided")
    exit()
r = requests.get(f"{url_root}/fiction/{book_id}")
soup = BeautifulSoup(r.content, "lxml")
title_div = soup.find("div", class_="fic-title")
title = title_div.div.h1.text
author = title_div.a.text
for chapter in soup.find_all("tr", class_="chapter-row"):
    chapter_link = chapter.a['href']
    chapter_name = chapter.a.text.strip()
    r = requests.get(url_root+chapter_link)
    filename = f"{title}/{chapter_name}.html"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as f:
        f.write(r.text)
    print(chapter_name)
