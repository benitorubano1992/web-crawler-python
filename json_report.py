import json

PATH_JSON = "report.json"

def write_json_report(page_data:dict, filename:str=PATH_JSON):
    pages = sorted(page_data.values(),key=lambda p:p["url"])
    try:
        with open(filename,"w", encoding="utf-8") as f:
            json.dump(pages,f,indent=2)
    
    except Exception as e:
        print(f"error writing file to {filename}, err: {str(e)}")
