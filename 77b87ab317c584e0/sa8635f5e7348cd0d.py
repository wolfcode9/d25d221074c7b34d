import sys
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import json
sys.path.append('..') 
from base.spider import Spider

class PTT:

    def __init__(self):
        self.url = "https://ptt.red/"
        self.extend = None

    def get_header(self):
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7"
        }

    def init(self, extend):
        self.extend = extend

    def home_content(self, filter=False):
        response = requests.get(self.url, headers=self.get_header())
        doc = BeautifulSoup(response.text, "html.parser")
        classes = []
        for a in doc.select("li > a.px-2.px-sm-3.py-2.nav-link"):
            classes.append({
                "id": a.get("href").replace("/p/", ""),
                "name": a.text
            })
        return json.dumps(classes)

    def category_content(self, tid, pg, filter=False, extend=None):
        builder = urljoin(self.url, f"p/{tid}")
        if extend:
            if "c" in extend:
                builder = urljoin(builder, f"c/{extend['c']}")
            if "area" in extend:
                builder += f"?area_id={extend['area']}"
            if "year" in extend:
                builder += f"&year={extend['year']}"
            if "sort" in extend:
                builder += f"&sort={extend['sort']}"
        builder += f"&page={pg}"
        
        response = requests.get(builder, headers=self.get_header())
        doc = BeautifulSoup(response.text, "html.parser")
        list = []
        for div in doc.select("div.card > div.embed-responsive"):
            a = div.select("a")[0]
            img = a.select("img")[0]
            remark = div.select("span.badge.badge-success")[0].text
            vodPic = img["src"] if img["src"].startswith("http") else urljoin(self.url, img["src"])
            list.append({
                "id": a["href"][1:],
                "title": img["alt"],
                "pic": vodPic,
                "remark": remark
            })
        return json.dumps(list)

    def detail_content(self, ids):
        response = requests.get(urljoin(self.url, ids[0]), headers=self.get_header())
        doc = BeautifulSoup(response.text, "html.parser")
        flags = {}
        playUrls = []
        for a in doc.select("ul#w1 > li > a"):
            flags[a["href"].split("/")[3]] = a["title"]
        items = doc.select("div > a.seq.border")
        for flag in flags:
            urls = []
            for e in items:
                urls.append(f"{e.text}${ids[0]}/{e['href'].split('/')[2]}/{flag}")
            if not urls:
                urls.append(f"1${ids[0]}/1/{flag}")
            playUrls.append("#".join(urls))
        vod = {
            "vodPlayFrom": "$$$".join(flags.values()),
            "vodPlayUrl": "$$$".join(playUrls)
        }
        return json.dumps(vod)

    def player_content(self, flag, id, vipFlags):
        response = requests.get(urljoin(self.url, id), headers=self.get_header())
        m = re.search(r'contentUrl":"(.*?)"', response.text)
        if m:
            return json.dumps({"url": m.group(1).replace("\\", "")})
        return json.dumps({"error": ""})

    def search_content(self, key, quick=False, pg="1"):
        response = requests.get(urljoin(self.url, f"q/{key}?page={pg}"), headers=self.get_header())
        doc = BeautifulSoup(response.text, "html.parser")
        list = []
        for div in doc.select("div.card > div.embed-responsive"):
            a = div.select("a")[0]
            img = a.select("img")[0]
            remark = div.select("span.badge.badge-success")[0].text
            vodPic = img["src"] if img["src"].startswith("http") else urljoin(self.url, img["src"])
            list.append({
                "id": a["href"][1:],
                "title": img["alt"],
                "pic": vodPic,
                "remark": remark
            })
        return json.dumps(list)
