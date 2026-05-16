from urllib.parse import urlsplit,urlparse,urljoin
from crawl import normalize_url,extract_page_data
import asyncio
import aiohttp
import requests
def get_html(url:str):
    try:
        response = requests.get(url, headers={"User-Agent": "BootCrawler/1.0"})
    except Exception as e:
        raise Exception(f"network error while fetching {url}: {e}")

    if response.status_code > 399:
        raise Exception(f"got HTTP error: {response.status_code} {response.reason}")

    content_type = response.headers.get("content-type", "")
    if "text/html" not in content_type:
        raise Exception(f"got non-HTML response: {content_type}")

    return response.text

def same_domain_page(base_url:str,current_url:str)->bool:
    base = urlsplit(base_url)
    current = urlsplit(current_url)
    return base.netloc == current.netloc


def crawl_page(base_url, current_url=None, page_data=None):
    if current_url is None:
        current_url = base_url
    if page_data is None:
        page_data ={}
    if not same_domain_page(base_url,current_url):
        return page_data
   
    current_normalize_url = normalize_url(current_url)
    if current_normalize_url in page_data:
        return page_data
    print(f"start crawling url: {current_url}")
    try:
        html_text = get_html(current_url)
        print(f"finished crawling url :{current_url}")
        result_extract = extract_page_data(html_text,current_url)
        page_data[current_normalize_url] = result_extract
        for link in result_extract["outgoing_links"]:
            page_data =crawl_page(base_url,link,page_data)

    except Exception as e:
        print(f"Error fetching url {current_url} : {str(e)}")

    return page_data

class AsyncCrawler():
    def __init__(self,base_url:str,max_concurrency:int,max_pages:int):
        self.base_url = base_url
        base = urlsplit(base_url)
        self.base_domain = base.netloc
        self.page_data={}
        self.lock = asyncio.Lock()
        self.max_concurrency =max_concurrency
        self.semaphore =asyncio.Semaphore(max_concurrency)
        self.session = None
        self.max_pages = max_pages
        self.all_tasks = set()
        self.should_stop = False
        self.seen_urls=set()
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    async def __aexit__(self, exc_type, exc, tb):
        await self.session.close()
    async def add_page_visit(self, normalized_url:str)->bool:
       async with self.lock:
            if self.should_stop:
                return False
            if  normalized_url in self.seen_urls:
                return False
            self.seen_urls.add(normalized_url)

            if len(self.page_data) >= self.max_pages:
                self.should_stop = True
                print("Reached maximum number of pages to crawl.")
                for task in self.all_tasks:
                    task.cancel()
                return False
            el = self.page_data.get(normalized_url,None)
            return el == None
    async def get_html(self,url:str):
        async with self.session.get(url) as resp:
            if resp.status > 399:
                raise Exception(f"got HTTP error: {resp.status} {resp.reason}")
            if "text/html" not in resp.content_type:
                raise Exception(f"got non-HTML response: {resp.content_type}")
            return await  resp.text()
    def _same_domain(self,current_url:str):
        base = urlsplit(self.base_url)
        current = urlsplit(current_url)
        return base.netloc == current.netloc

    
    async def crawl_page(self,current_url:str):
        if current_url is None:
            current_url = self.base_url
        if self.should_stop:
            return 
        if not self._same_domain(current_url):
            return
        current_normalize_url = normalize_url(current_url)
        if not  await self.add_page_visit(current_normalize_url):
            return
        
        print(f"start crawling url: {current_url}")
        async with self.semaphore:
            try:
                html_text = await self.get_html(current_url)
                result_extract = extract_page_data(html_text,current_url)
                async with self.lock:
                    if self.should_stop:
                        return
                    if len(self.page_data) >= self.max_pages:
                        self.should_stop = True
                        print("Reached maximum number of pages to crawl.")
                        for task in self.all_tasks:
                            task.cancel()
                        return
                    
                    self.page_data[current_normalize_url]=result_extract
               
            except Exception as e:
                print(str(e))
               
                return
        tasks = set()
        for link in result_extract["outgoing_links"]:
            task = asyncio.create_task(self.crawl_page(link))
            tasks.add(task)
            self.all_tasks.add(task)
        try:
            await asyncio.gather(*tasks,return_exceptions=True)
        except Exception as e:
            print(f"Error gathering tasks {str(e)}")
        finally:
            for task in tasks:
                self.all_tasks.discard(task)
        
           
    async def crawl(self):
        await self.crawl_page(self.base_url)
        return self.page_data
    
async def crawl_site_async(url:str,maxConcurrency:int,max_pages:int):
    async with AsyncCrawler(url,maxConcurrency,max_pages) as a:
        return await a.crawl()




        
        






    

    
    