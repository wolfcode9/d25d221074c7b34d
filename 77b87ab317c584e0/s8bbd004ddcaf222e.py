#coding=utf-8
#!/usr/bin/python
import sys
sys.path.append('..') 
from base.spider import Spider
import concurrent.futures
import datetime
import json

class Spider(Spider):
	
	siteUrl = ""
	headers = {}
	headers["User-Agent"] = "okhttp/3.12.0"
	#headers["Referer"] = siteUrl

	# 設置年份範圍	
	current_year = datetime.datetime.now().year 
	years = [{"n": f"{year}", "v": f"{year}"} for year in range(current_year, current_year - 12, -1)]
	#
	config = {
		"player": {},
		"filter": [
			{"key": "region", "name": "地區", "value": [
				{"n": "全部", "v": ""},
				{"n": "大陸", "v": "大陸"},
				{"n": "歐美", "v": "歐美"},
				{"n": "日本", "v": "日本"},
				{"n": "臺灣", "v": "臺灣"},
				{"n": "香港", "v": "香港"},
				{"n": "韓國", "v": "韓國"},
				{"n": "新馬泰", "v": "新馬泰"},
				{"n": "其他", "v": "其他"}
			]},
			{"key": "year", "name": "年份", "value": [
				{"n": "全部", "v": ""},
				*years
			]}
		]
	}
	
	
	#命名
	def getName(self):
		return "UBVod"
	
	
	def init(self,extend):
		try:
			data = json.loads(extend)
			self.siteUrl = data["url"]
			self.vip = data["vip"]

		except Exception as ex:
			print(ex)
		
	
	#主頁
	def homeContent(self, filter):

		if self.vip:
			classes = [{"type_id": "108", "type_name": "成人" }]
		else:
			classes = [
				{"type_id": "100", "type_name": "電影"}, 
				{"type_id": "101", "type_name": "電視劇"},
				{"type_id": "102", "type_name": "綜藝"}, 
				{"type_id": "103", "type_name": "動漫" },
				{"type_id": "105", "type_name": "紀實" },		
			]

		result = {"filters": {item["type_id"]: self.config["filter"] for item in classes}, "class": classes}
		return result
	
	
	#推薦頁
	def homeVideoContent(self):	
		result = {}	
	
		url = f"{self.siteUrl}/api/vod?vip={self.vip}"

		try:
			response = self.fetch(url=url)
			result = response.json()

		except Exception as ex:
			print(ex)

		return result
	
	
	#分類頁
	def categoryContent(self, tid, pg, filter, extend):		
		result = {}
		url = f"{self.siteUrl}/api/vod/list"
		
		params = {
			"type_id": tid,
			"page": pg,
			"vod_area": extend.get("region"),
			"vod_year": extend.get("year"),			
		}
		
		try:
			response = self.fetch(url=url,params=params)
			result = response.json()
			result["page"] = pg

		except Exception as ex:
			print(ex)
		
		return result	
	
	#搜索頁1
	def searchContent(self, key, quick):
		result = {}	
		result = self.searchContentPage(key=key, quick=quick)
		return result
	
	#搜索頁2
	def searchContentPage(self, key, quick, pg="1"):
		result = {}
		url = f"{self.siteUrl}/api/vod/list?wb={key}"

		try:
			response = self.fetch(url=url)
			result = response.json()		

		except Exception as ex:
			print(ex)
		
		return result	

	
	#詳情頁
	def detailContent(self, ids):
		result = {}
		vod_id = ids[0]
		url = f"{self.siteUrl}/api/vod/detail?vod_id={vod_id}"

		try:
			response = self.fetch(url=url)
			result = response.json()		

		except Exception as ex:
			print(ex)
		
		return result	
	

	#播放頁
	def playerContent(self, flag, id, vipFlags):
		ids = id.split("_")
		vod_id = ids[0]
		vod_fragment_id = ids[1]
		url = f"{self.siteUrl}/api/vod/source?vod_id={vod_id}&vod_fragment_id={vod_fragment_id}"
		vod_url = ""
		try:
			response = self.fetch(url=url)
			vod_url = response.text
		except Exception as ex:
			print(ex)
		
		HOST = f"{vod_url.split('//')[1].split('/')[0]}"		
		#self.headers["User-Agent"] = "ExoSourceManager/1.0.3 (Linux;Android 10) ExoPlayerLib/2.11.3"
		#self.headers["allowCrossProtocolRedirects"] = True
		self.headers["Accept-Encoding"] = "gzip" 
		self.headers["Host"] = HOST
		self.headers["Connection"] = "Keep-Alive"
		result = {
			"parse": "0",
			"playUrl": "",
			"url": vod_url,
			"header": self.headers
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