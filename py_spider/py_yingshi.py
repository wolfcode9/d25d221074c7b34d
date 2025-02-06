#coding=utf-8
#!/usr/bin/python
#Updated: 2025.01.20
#Web Site: https://www.yingshi.tv/

import sys
import requests
from datetime import datetime
from base.spider import Spider

class Spider(Spider):
    apiurl =  "https://api.yingshi.tv"

    # 設置年份範圍	
    current_year = datetime.now().year
    years = [{"n": f"{year}", "v": f"{year}"} for year in range(current_year, current_year - 13, -1)]
    years.insert(0, {"n": "全部", "v": ""})    
    
    filters = [
        {
            "key": "region","name": "地區",
            "value": [
                {"n": "全部", "v": ""},
                {"n": "大陸", "v": "大陸"},
                {"n": "歐美", "v": "歐美"},
                {"n": "日本", "v": "日本"},
                {"n": "臺灣", "v": "臺灣"},
                {"n": "香港", "v": "香港"},
                {"n": "韓國", "v": "韓國"},
                {"n": "新馬泰", "v": "新馬泰"},
                {"n": "其他", "v": "其他"}
            ]
        },
        {"key": "year","name": "年份","value": years}
    ]

    #命名
    def getName(self):
        return "YingShi"

    def init(self, extend):         
        self.extend = extend
    
    def fetch_json(self, url, params=None):
        try:
            rsp = requests.get(url, params=params).json()
            return rsp
        except requests.RequestException as e:
            print(f"Error fetching data from {url}: {e}")
            return {}
    # 主頁
    def homeContent(self, filter):
        result = {}
        classes = [
            {"type_id": "2", "type_name": "電影"}, 
            {"type_id": "1", "type_name": "電視劇"},
            {"type_id": "3", "type_name": "綜藝"}, 
            {"type_id": "4", "type_name": "動漫"},
            {"type_id": "5", "type_name": "記錄片"}
        ]
        result = {"filters": {item["type_id"]: self.filters for item in classes}, "class": classes}
        return result

    # 推薦頁
    def homeVideoContent(self):
        result = {}
        url = f'{self.apiurl}/page/v4.5/typepage?id=0'
        rsp = self.fetch_json(url)
        data = rsp.get("data", "")
        if data.get("yunying"):
            result["list"] = data["yunying"][0]["vod_list"]
        return result

    # 分類頁
    def categoryContent(self, tid, pg, filter, extend):
        url = f'{self.apiurl}/vod/v1/vod/list'
        params = {
            "order": "desc",
            "tid": tid,
            "page": pg,
            "limit": "30",
            "by": "time",
            "class": extend.get("class", ""),
            "year": extend.get("year", ""),
            "lang": extend.get("lang", ""),
            "area": extend.get("area", "")
        }
        rsp = self.fetch_json(url, params)
        data = rsp.get("data", "")
        result = {
            'list': data.get("List", []),
            'page': pg,
            'pagecount': data.get('TotalPageCount', 0),
            'limit': 30,
            'total': data.get('Total', 0)
        }
        return result

    # 搜索頁
    def searchContent(self, key, quick="", pg="1"):
        url = f'{self.apiurl}/vod/v1/search?wd={key}&limit=20&page={pg}'
        result = {}
        rsp = self.fetch_json(url)
        data = rsp.get("data", "")
        result['list'] = data.get("List", [])
        return result

    # 詳情頁
    def detailContent(self, ids):
        id = ids[0]
        result = {}        
        url = f'{self.apiurl}/vod/v1/info?id={id}'
        rsp = self.fetch_json(url)
        data = rsp.get("data", "")
        sources = data.get("vod_sources", [])
        playGroups = []
        groupNames = []
        for source in sources:            
            groupNames.append(source["source_name"])
            groupUrls = []
            for v in source["vod_play_list"]['urls']:
                episode_name = v['name']
                groupUrls.append(f"{episode_name}${v['url']}")

            playGroups.append('#'.join(groupUrls))

        vod_play_url = '$$$'.join(playGroups)
        vod_play_from = '$$$'.join(groupNames)
        result = {
            'list': [{
                "vod_id": data.get("vod_id", ""),
                "vod_name": data.get("vod_name", ""),
                "vod_pic": data.get("vod_pic", ""),
                "vod_remarks": data.get("vod_remarks", ""),
                "type_name": data.get("vod_class", ""),
                "vod_year": data.get("vod_year", ""),
                "vod_area": data.get("vod_area", ""),
                "vod_actor": data.get("vod_actor", ""),
                "vod_director": data.get("vod_director", ""),
                "vod_content": data.get("vod_content", ""),
                "vod_play_from": vod_play_from,
                "vod_play_url": vod_play_url
            }]
        }
        return result

    # 播放頁
    def playerContent(self, flag, id, vipFlags):
        return {
            'parse': '0',
            'playUrl': '',
            'url': id,
            'header': ''
        }

    # 釋放資源
    def destroy(self):
        pass

    # 視頻格式
    def isVideoFormat(self, url):
        pass

    # 視頻檢測
    def manualVideoCheck(self):
        pass

    # 本地代理
    def localProxy(self, param):
        action = {
            "url": "",
            "header": "",
            "param": "",
            "type": "string",
            "after": ""
        }
        return [200, "video/MP2T", action, ""]