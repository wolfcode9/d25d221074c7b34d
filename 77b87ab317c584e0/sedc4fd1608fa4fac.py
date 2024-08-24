#coding=utf-8
#!/usr/bin/python
import sys
sys.path.append('..') 
from base.spider import Spider
import concurrent.futures

class Spider(Spider):

    def getName(self):
        return "豆瓣薦片"

    def init(self, extend):
        pass

    def homeContent(self, filter):
        classes = [
            {"type_id": "tv", "type_name": "熱播劇集"},
            {"type_id": "movie", "type_name": "熱播電影"}
        ]
        return {'class': classes}

    def homeVideoContent(self):
        limit = 10
        urls = [
            self.douban_url('movie', limit, 0),
            self.douban_url('tv', limit, 0)
        ]
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.fetch_vodData, url) for url in urls]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # 合併結果列表
        combined_results = [item for sublist in results for item in sublist]
        return {'list': combined_results}

    def categoryContent(self, tid, pg, filter, extend):
        limit = 20
        start = (int(pg) - 1) * limit
        total = 1000
        pagecount = total // limit
        vod_data = self.fetch_vodData(self.douban_url(tid, limit, start))
        return {
            'list': vod_data,
            'limit': limit,
            'page': pg,
            'pagecount': pagecount,
            'total': total
        }

    def detailContent(self, array):
        return {}

    def searchContent(self, key, quick):
        return {}

    def searchContentPage(self, key, quick, pg):
        pass

    def playerContent(self, flag, id, vipFlags):
        return {}

    def destroy(self):
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def localProxy(self, param):
        action = {
            'url': '',
            'header': '',
            'param': '',
            'type': 'string',
            'after': ''
        }
        return [200, "video/MP2T", action, ""]

    def douban_url(self, typeid, limit, pg):
        base_url = 'https://movie.douban.com/j/search_subjects'
        return f'{base_url}?type={typeid}&tag=热门&page_limit={limit}&page_start={pg}'

    def fetch_vodData(self, url):
        vod = []
        header = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        jsonData = self.fetch(url=url, headers=header).json()
        for v in jsonData['subjects']:
            remarks = v['episodes_info'] or v['rate']
            vod.append({
                "vod_id": '',
                "vod_name": v['title'],
                "vod_pic": v['cover'],
                "vod_remarks": remarks
            })
        return vod