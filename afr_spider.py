"""
Author: Tim Zhang
Date: 08/04/2020
Disclaimer: This is only for education purpose. Please do not use it to violate any copyright laws

"""

import requests
from lxml import html
from datetime import datetime, timedelta
import json
import pandas as pd

SITE_URL = "https://www.afr.com"
SEARCH_URL = "https://www.afr.com/public/ffx/search"


def search_for_artiles_by_date(date):
    requested_date = datetime.strptime(date, "%Y-%m-%d")
    start_date = requested_date - timedelta(days=1)
    end_date = requested_date

    search_params = {
        "keywords": "",
        "startDate": start_date.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        "endDate": end_date.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        "offTime": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        "limit": 10,
        "offset": 0,
        "dateType": 0,
        "brands": ["/etc/tags/ffx-brands/afr"],
        "order": "Date",
        "searchText": "",
    }
    search_payload = {
        "data": json.dumps(search_params)
    }

    search_headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "origin": "https://www.afr.com",
        "referer": "https://www.afr.com/search.html?text=&ss=afr.com.au",
        "x-requested-with": "XMLHttpRequest",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    }

    r = requests.post(SEARCH_URL, data=search_payload, headers=search_headers)

    result_dict = r.json()
    urls_list = []
    for article in result_dict["assets"]:
        urls_list.append(SITE_URL + article["href"])
    return urls_list


def parse_article(url):
    page = requests.get(url)
    tree = html.fromstring(page.content)

    article = {}
    article["title"] = tree.xpath("//head//meta[@property='og:title']/@content")[0]
    article["published_date"] = tree.xpath("//head//meta[@property='article:published_time']/@content")[0]
    author_meta = tree.xpath("//head//meta[@name='parsely-author']/@content")
    article["author"] = author_meta[0] if author_meta else ''
    article["summary"] = tree.xpath("//head//meta[@property='og:description']/@content")[0]
    article["body"] = "".join([t.text for t in tree.xpath("//section//p") if t.text])
    return article


def parse_articles_list(urls_list):
    articles_list = []
    for url in urls_list:
        article = parse_article(url)
        articles_list.append(article)
    return articles_list


def save_to_csv(articles_list):
    df = pd.DataFrame(articles_list)
    print(f"{len(articles_list)} articles extracted!")
    return df.to_csv("afr_extract.csv", index=False)


def main():
    article_urls = search_for_artiles_by_date("2020-04-08")
    articles_list = parse_articles_list(article_urls)
    save_to_csv(articles_list)


if __name__ == "__main__":
    main()
