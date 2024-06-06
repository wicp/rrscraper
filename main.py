import sys
import os
from bs4 import BeautifulSoup
from ebooklib import epub
import requests

def create_epub(id,author,title):
    book = epub.EpubBook()

    book.set_identifier(id)
    book.set_title(title)
    book.set_language("en")
    book.add_author(author)

    chapters = []
    for file in os.scandir(f"./{title}"):
        if file.path.endswith(".html"):
            with open(file, 'r') as f:
                soup = BeautifulSoup(f, "lxml")
                chapter_title = os.path.basename(file).split('.')[0]
                chapter = epub.EpubHtml(title=chapter_title, file_name=f"{chapter_title}.xhtml", lang="en")
                chapter.content = str(soup.find("div", class_="chapter-content"))
            chapters.append(chapter)
            book.add_item(chapter)

    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    book.toc = tuple(chapters)

    # define css style
    style = '''
    @namespace epub "http://www.idpf.org/2007/ops";

    body {
        font-family: Cambria, Liberation Serif, Bitstream Vera Serif, Georgia, Times, Times New Roman, serif;
    }

    h2 {
         text-align: left;
         text-transform: uppercase;
         font-weight: 200;     
    }

    ol {
            list-style-type: none;
    }

    ol > li:first-child {
            margin-top: 0.3em;
    }


    nav[epub|type~='toc'] > ol > li > ol  {
        list-style-type:square;
    }


    nav[epub|type~='toc'] > ol > li > ol > li {
            margin-top: 0.3em;
    }

    '''

        # add css file
    nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
    book.add_item(nav_css)
    book.spine = ["nav", *chapters]
    epub.write_epub(f"{title}.epub", book, {})

if __name__ == "__main__":
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
    print(f"Writing {title}.epub...")
    create_epub(book_id,author,title)

