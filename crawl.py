from urllib.parse import urlsplit,urlparse,urljoin
from bs4 import BeautifulSoup
def normalize_url(url:str)->str:
    o = urlsplit(url)
    result = o.netloc + o.path
    if result.endswith("/"):
        result=result[:-1]
    return result.lower()

def get_heading_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    h1 = soup.find("h1")
    if h1 is not None:
        return h1.get_text(strip=True)
    h2 = soup.find("h2")
    if h2 is not None:
        return h2.get_text(strip=True)
    return ""
def get_first_paragraph_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')

    main = soup.find("main")
    result=""
    if main is not None:
        p = main.find("p")
        if p is not None:
            result = p.get_text(strip=True)
    if result == "":
        p = soup.find("p")
        if p is not None:
            result = p.get_text(strip=True)
    return result
    
def is_absolute(url):
    return bool(urlparse(url).netloc)

def get_urls_from_html(html, base_url)->list[str]:
    soup = BeautifulSoup(html, 'html.parser')
    body = soup.find("body")
    if body is not None:
        a_list = body.find_all("a")
    else:
        a_list = soup.find_all("a")
    result=[]
    for i in range(len(a_list)):
        a_tag = a_list[i]
        href = a_tag.get("href")
        try:
            absolute_url = urljoin(base_url, href)
            result.append(absolute_url)
        except Exception as e:
            print(f"{str(e)}: {href}")
    return result
def get_images_from_html(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    body = soup.find("body")
    if body is not None:
        img_list = body.find_all("img")
    else:
        img_list = soup.find_all("img")
    result=[]
    for i in range(len(img_list)):
        img = img_list[i]
        src = img.get("src")
        try:
            absolute_url = urljoin(base_url, src)
            result.append(absolute_url)
        except Exception as e:
            print(f"{str(e)}: {src}")
    return result

def extract_page_data(html, page_url):
        return {
             "url":page_url,
             "heading":get_heading_from_html(html),
             "first_paragraph":get_first_paragraph_from_html(html),
             "outgoing_links":get_urls_from_html(html,page_url),
             "image_urls":get_images_from_html(html,page_url)
        }
    




