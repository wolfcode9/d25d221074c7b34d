seeare#coding=utf-8
#!/usr/bin/python
import sys
sys.path.append('..') 
from base.spider import Spider
import concurrent.futures
import datetime

class Spider(Spider):
	
	siteUrl = "http://192.168.1.9:8989" #"http://210.61.186.128:8989"
	header = {
		"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer":  siteUrl
	}

	current_year = datetime.datetime.now().year
	# 設置年份範圍
	years = [{"n": f"{year}", "v": f"{year}"} for year in range(current_year, current_year - 12, -1)]
	# 配置字典
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
		pass
	
	#主頁
	def homeContent(self,filter):
		classes = [
			{"type_id": "100", "type_name": "電影"}, 
			{"type_id": "101", "type_name": "電視劇"},
			{"type_id": "102", "type_name": "綜藝"}, 
			{"type_id": "103", "type_name": "動漫" },
			{"type_id": "105", "type_name": "紀實" },
			{"type_id": "107", "type_name": "少兒" },
			{"type_id": "108", "type_name": "成人" },
		]
		result = {"filters": {},"class":classes}
		if filter:
			for item in classes:    
				result["filters"][item["type_id"]] = self.config["filter"]
		return result
	
	#推薦頁
	def homeVideoContent(self):		
		result = {}	
		return result
		
	
	#分類頁
	def categoryContent(self,tid,pg,filter,extend):		
		result = {}	
		vod = []			
		url = "http://192.168.1.9:8989/api/video/list"
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
			video_list = jrsp["data"]["video_list"]
			for v in video_list:
				vod.append({
					"vod_id": v["id"],
					"vod_name": v["title"],
					"vod_pic": v["pic"],
					"vod_remarks": v["state"]
            	})
			result["list"] = vod
			result["page"] = pg
			result["pagecount"] = 9999
			result["limit"] = pagesize
			result["total"] = 999999
		return result 
	
	#詳情頁
	def detailContent(self, array):		
		result = {}        
		video_id = array[0]
		url = f"http://192.168.1.9:8989/api/video/info?video_id={video_id}"
		jrsp = self.fetch(url=url).json()		
		if jrsp.get("video"):
			vod = jrsp["video"]


			result['list'] = [{
				"type_name": "",
				"vod_id": vod.get('id', ''),
				"vod_name": vod.get('title', ''),
				"vod_pic": vod.get('pic', ''),
				"vod_remarks": vod.get('state', ''),                
				"vod_year": vod.get('year', ''),
				"vod_area": vod.get('region', ''),
				"vod_director": vod.get('director', ''),                
				"vod_actor": vod.get('starring', ''),                
				"vod_play_from": "UBVod",
				"vod_play_url": "",
				"vod_content": "",                
				"vod_tag": ""
			}]
		return result
	
	def searchContentPage(self, key, quick, pg):
		pass
	
	def destroy(self):
		pass

	#搜索頁
	def searchContent(self,key,quick):
		result = {}
		return result
	
	#播放頁
	def playerContent(self,flag,id,vipFlags):		
		video_id = id.split("#")[0]
		video_fragment_id = id.split("#")[1]
		url = f"http://192.168.1.9:8989/api/video/source?video_id={video_id}&video_fragment_id={video_fragment_id}"
		jrsp = self.fetch(url=url).json()		
		if jrsp.get("data"):
			source_url = jrsp["data"]["video_soruce"]["url"].split("?")[0]
			result = {
				'parse': '0',
				'playUrl': '',
				'url': source_url,
				'header': ''
			}
		return result
	
	#視頻格式
	def isVideoFormat(self,url):
		pass
	
	#視頻檢測
	def manualVideoCheck(self):
		pass
	
	#本地代理
	def localProxy(self,param):
		action = {
			'url':'',
			'header':'',
			'param':'',
			'type':'string',
			'after':''
		}
		return [200, "video/MP2T", action, ""]	
	

#sp = Spider()
#print(sp.homeVideoContent())
#print(sp.categoryContent(101,1,None,None))
#print(sp.detailContent(['75983']))
#print(sp.fetch_video_source(video_id=75983,video_fragment=470610))
