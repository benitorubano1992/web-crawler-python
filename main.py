import sys
import asyncio
from get_html import get_html,crawl_page,crawl_site_async
from json_report import write_json_report

DEFAULT_MAX_CONCURRENCY = 3
DEFAULT_MAX_PAGES = 10

def get_max_concurrency(arg:str):
    try:
        value = int(arg)
        if value < 0:
            return DEFAULT_MAX_CONCURRENCY
        return value
    except Exception as e:
        print(f"invalid max concurrency {str(e)}")
        return DEFAULT_MAX_CONCURRENCY

def get_max_pages(args:str):
    try:
        value = int(arg)
        if value < 0:
            return DEFAULT_MAX_PAGES
        return value
    except Exception as e:
        print(f"invalid max concurrency {str(e)}")
        return DEFAULT_MAX_PAGES



async def main_async():
    args = sys.argv[1:]
    if len(args) == 0:
        print("no website provided")
        sys.exit(1)
    url_crawl = args[0]
    max_concurrency = DEFAULT_MAX_CONCURRENCY
    max_pages = DEFAULT_MAX_PAGES
    if len(args[1:]) >= 1:
        max_concurrency = get_max_concurrency(args[1])
    if len(args[1:]) >= 2:
        max_pages = get_max_pages(args[2])
    
    print(f"url:{url_crawl},concurrency:{max_concurrency}, max_pages:{max_pages}")


    #print(f"starting crawl of: {url_crawl}")
    #print(get_html(url_crawl))
    page_data = await crawl_site_async(url_crawl,max_concurrency,max_pages)
    print(f"num_pages_found: {len(page_data)}")
    #for page in page_data.values():
        #print(f"Found {len(page['outgoing_links'])} outgoing links on {page['url']}")
    write_json_report(page_data,"report.json")


    


if __name__ == "__main__":
    asyncio.run(main_async())
