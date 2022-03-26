import requests
import warnings
import dateparser, time
from lxml import html

from db import WebparserDB
from tools import *


headers = {"User-Agent": "Mozilla/5.001 (linux; U; NT4.0; en-US; rv:1.0) Gecko/25250101"}
timeout = 15

def main():
    start_time = time.time()
    items = []
    # ignore warning from dateparser library
    warnings.filterwarnings(
        "ignore",
        message="The localize method is no longer necessary, as this time zone supports the fold attribute",
    )

 
    with WebparserDB() as db:
        resource = db.query("SELECT * FROM `resource`")
        for row in resource:
            id, name, url, top_tag, bottom_tag, title_cut, date_cut = row 
            # if id < 4:
            #     continue

            last_link = ""

            tree = request_htmltree(url)
            if tree is None:
                continue
            print(f"Парсинг ресурса < {id} > {url}")
            links = tree.xpath(top_tag)
            existing_links =  [r[0] for r in db.query("SELECT link FROM `items` WHERE `res_id` = %s", (id,))]
    
            for id, link in enumerate(links):
                link = make_absolute_url(url, link)
                print_inline(link, last_link)
                if link in existing_links:
                    continue

                item = fetch_item(id, url, link, bottom_tag, title_cut, date_cut)
                if not item:
                    continue

                items.append(item)
                last_link = link
            db.save_items(items)
            items.clear()
            print_inline("", last_link)
        print()       
    print(f"Завершино сайтов: {len(resource)}")
    print(f"Время: {round(time.time() - start_time, 1)} секунд")



def request_htmltree(url):
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return html.fromstring(response.content)

    except Exception as e:
        print()
        print(f'Не удалось спарсить: "{url}"')
        print(e)
        print()
        return 


def fetch_item(res_id, url, link, bottom_tag, title_cut, date_cut):
    inner_tree = request_htmltree(link)
    if inner_tree is None:
        return
    date_time = dateparser.parse(inner_tree.xpath(date_cut)[0])

    title = ''.join(inner_tree.xpath(title_cut))
    content = ''.join(inner_tree.xpath(bottom_tag))
    not_date = date_time.strftime('%Y-%m-%d')
    nd_date = date_time.timestamp()
    
    return {
        "res_id": res_id,
        "link": link,
        "title": title,
        "content": content,
        "nd_date": nd_date,
        "not_date": not_date}






if __name__ == "__main__":
    main()

