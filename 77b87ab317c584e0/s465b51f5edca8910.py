#coding=utf-8
#!/usr/bin/python
#Updated 2025.01.20
import sys
sys.path.append('..') 
from base.spider import Spider
import requests
from datetime import datetime


class Spider(Spider):
	current_year = datetime.now().year
	years = [{"n": f"{year}", "v": f"{year}"} for year in range(current_year, current_year - 13, -1)]
	years.insert(0, {"n": "全部", "v": ""})
	config = {
        "player": {},
        "filter": [
            {
                "key": "region",
                "name": "地區",
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
            {
                "key": "year",
                "name": "年份",
                "value": years
            }
        ]
    }


	#命名
	def getName(self):
		return "影視"

	
	def init(self,extend={}):		
		self.extend = extend	

	
	#主頁
	def homeContent(self,filter):		
		result = {}				
		classes = [
			{"type_id": "2", "type_name": "電影"}, 
			{"type_id": "1", "type_name": "電視劇"},
			{"type_id": "3", "type_name": "綜藝"}, 
			{"type_id": "4", "type_name": "動漫" },
			{"type_id": "5", "type_name": "記錄片" }
		]		
		result = {"filters": {item["type_id"]: self.config["filter"] for item in classes}, "class": classes}		
		return result
	
	#推薦頁
	def homeVideoContent(self):		
		result  = {}		
		url = "https://api.yingshi.tv/page/v4.5/typepage?id=0"
		rsp = self.fetch(url).json()
		data = rsp.get("data","")
		if data:
			result["list"] = data["yunying"][0]["vod_list"]
		return result


	#分類頁	
	def categoryContent(self, tid, pg, filter, extend):			
		#https://api.yingshi.tv/vod/v1/vod/list?order=desc&limit=30&tid=1&by=time&class=%E5%81%B6%E5%83%8F&area=%E5%A4%A7%E9%99%86&lang=%E5%9B%BD%E8%AF%AD&year=2024&page=1
		url = f"https://api.yingshi.tv/vod/v1/vod/list"
		result = {}	
		params = {
			"order":"desc",
			"tid": tid,
			"page": pg,
			"limit": "30",			
			"by": "time",
			"class": extend.get("class", ""),
			"year": extend.get("year", ""),
			"lang": extend.get("lang", ""),
			"area": extend.get("area", "")			
		}		
		rsp = requests.get(url=url,params=params).json()
		data =rsp.get("data","")
		result['list'] = data["List"]
		result['page'] = pg
		result['pagecount'] = data['TotalPageCount']
		result['limit'] = 30
		result['total'] = data['Total']
		return result

	
	#搜索頁
	#https://api.yingshi.tv/vod/v1/search?wd=123&limit=20&page=1
	def searchContent(self, key, quick="", pg="1"):
		url = f"https://api.yingshi.tv/vod/v1/search?wd={key}&limit=20&page=1"
		result = {}
		rsp =  self.fetch(url).json()
		data = rsp.get("data","")		
		result['list'] = data["List"]
		return result

	
	#詳情頁
	def detailContent(self, ids):
		#https://api.yingshi.tv/vod/v1/info?id=207690		
		result = {}		
		vod_id = ids[0]
		url = f"https://api.yingshi.tv/vod/v1/info?id={vod_id}"
		rsp =  self.fetch(url).json()
		data = rsp.get("data","")
		sources =  data.get("vod_sources","")

		playUrls = []
		for source in  sources:
			if "国内" in source["source_name"] :			
				for v in source["vod_play_list"]['urls']:
					playUrls.append('#'.join([v['name'] + '$' + v['url']]))
				break
			
		result = {'list': [{
			"vod_id": data.get("vod_id",""),
			"vod_name": data.get("vod_name",""),
			"vod_pic": data.get("vod_pic",""),
			"vod_remarks": data.get("vod_remarks",""),
			"type_name": data.get("vod_class",""),
			"vod_year": data.get("vod_year",""),
			"vod_area": data.get("vod_area",""),
			"vod_actor": data.get("vod_actor",""),
			"vod_director": data.get("vod_director",""),
			"vod_content": data.get("vod_content",""),
			"vod_play_from": "✡️",			
			"vod_play_url": '#'.join(playUrls)
		}]}
		return result

	
	#播放頁
	def playerContent(self, flag, id, vipFlags):
		result = {
        	'parse': '0',
            'playUrl': '',
            'url': id,
            'header': ''
        }
		return result

	
	#釋放資源
	def destroy(self):
		pass

	
	#視頻格式
	def isVideoFormat(self, url):
		pass

	
	#視頻檢測
	def manualVideoCheck(self):
		pass


	#本地代理
	def localProxy(self, param):
		action = {
			"url": "",
			"header": "",
			"param": "",
			"type": "string",
			"after": ""
		}
		return [200, "video/MP2T", action, ""]
