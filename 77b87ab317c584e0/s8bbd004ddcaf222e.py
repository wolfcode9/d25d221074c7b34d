#coding=utf-8
#!/usr/bin/python
import sys
sys.path.append('..') 
from base.spider import Spider
import concurrent.futures
import datetime

class Spider(Spider):
	
	siteUrl = "http://210.61.186.128:8989" 
	header = {
		"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer":  siteUrl
	}

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
	
	def init(self,extend=""):
		self.extend = extend		
		print("============{0}============".format(extend))		
	
	#主頁
	def homeContent(self, filter):
		classes = [
			{"type_id": "100", "type_name": "電影"}, 
			{"type_id": "101", "type_name": "電視劇"},
			{"type_id": "102", "type_name": "綜藝"}, 
			{"type_id": "103", "type_name": "動漫" },
			{"type_id": "105", "type_name": "紀實" },
			{"type_id": "107", "type_name": "少兒" },
			{"type_id": "108", "type_name": "成人" },
		]
		result = {"filters": {item["type_id"]: self.config["filter"] for item in classes}, "class": classes}
		return result
	
	#推薦頁
	def homeVideoContent(self):		
		result = {}			
		video = []			
		url_movie = "{}/api/video/recommend?parent_category_id=100&page=1&pagesize=20&kind=0".format(self.siteUrl)
		url_tv = "{}/api/video/recommend?parent_category_id=101&page=1&&pagesize=20&kind=0".format(self.siteUrl)
		with concurrent.futures.ThreadPoolExecutor() as executor:                    
			jrsp_movie = executor.submit(self.fetch, url_movie).result().json().get("video_hot_list")
			jrsp_tv = executor.submit(self.fetch, url_tv).result().json().get("video_hot_list")
			vdata = (jrsp_movie or []) + (jrsp_tv or [])

		for vod in vdata:			
			video.append({				
				"vod_id": vod["id"],
				"vod_name": vod["title"],
				"vod_pic": vod["pic"],
				"vod_remarks": vod["state"]				
			})			      
		result["list"] = video
		
		return result
		
	
	#分類頁
	def categoryContent(self, tid, pg, filter, extend):		
		result = {}	
		video = []			
		url = "{}/api/video/list".format(self.siteUrl)		
		pagesize = 35
		
		params = {
			"parent_category_id": tid,
			"page": pg,
			"region": extend.get("region", ""),
			"year": extend.get("year", ""),
			"pagesize": pagesize			
		}		
		jrsp = self.fetch(url=url,params=params).json()
		if jrsp.get("data"):
			vdata = jrsp["data"]["video_list"]
			for vod in vdata:
				video.append({
					"vod_id": vod["id"],
					"vod_name": vod["title"],
					"vod_pic": vod["pic"],
					"vod_remarks": vod["state"]
            	})
			result["list"] = video
			result["page"] = pg
			result["pagecount"] = 9999
			result["limit"] = pagesize
			result["total"] = 999999
		return result 
	
	#搜索頁(舊)
	def searchContent(self, key, quick):
		return self.searchContentPage(key, quick, "1")		
	
	#搜索頁(新)
	def searchContentPage(self, key, quick, pg):
		result = {}	
		video = []			
		url = "{}/api/video/list".format(self.siteUrl)
		pagesize = 35
		params = {
			"keyword": key,
			"page": 1,			
			"pagesize": pagesize			
		}		
		jrsp = self.fetch(url=url,params=params).json()
		if jrsp.get("data"):
			vdata = jrsp["data"]["video_list"]
			for vod in vdata:
				video.append({
					"vod_id": vod["id"],
					"vod_name": vod["title"],
					"vod_pic": vod["pic"],
					"vod_remarks": vod["state"]
            	})
			result["list"] = video
		return result 
	
	#詳情頁
	def detailContent(self, ids):
		result = {}
		video_id = ids[0]
		url = "{}/api/video/info?video_id={}".format(self.siteUrl,video_id)
		jrsp = self.fetch(url=url).json()

		if jrsp.get("video"):
			vod = jrsp["video"]
			video = []
			vod_play_urls  = ""
			for vf in jrsp.get("video_fragment_list"):
				vod_play_urls += "{}${}_{}#".format(vf["symbol"], video_id, vf["id"])

			video.append ({			
				"type_name": "",
				"vod_id": vod.get("id", ""),
				"vod_name": vod.get("title", ""),		
				"vod_remarks": vod.get("description", ""),
				"vod_year": vod.get("year", ""),
				"vod_area": vod.get("region", ""),
				"vod_actor": vod.get("starring", ""),
				"vod_director": vod.get("director", ""),
				"vod_content": "",	
				"vod_play_from": "UBVod",
				"vod_play_url": vod_play_urls.strip('#')
			})
			result['list'] = video

		return result

	#播放頁
	def playerContent(self, flag, id, vipFlags):
		ids = id.split("_")
		video_id = ids[0]
		video_fragment_id = ids[1]
		url = "{}/api/video/source?video_id={}&video_fragment_id={}".format(self.siteUrl,video_id,video_fragment_id)
		jrsp = self.fetch(url=url).json()		
		if jrsp.get("data"):
			source_url = jrsp["data"]["video_soruce"]["url"].split("?")[0]
			result = {
				"parse": "0",
				"playUrl": "",
				"url": source_url,
				"header": self.header
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