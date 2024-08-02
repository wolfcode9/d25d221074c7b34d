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
	vip = 0
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

	
	def vod_remark(self,vod={}):
		parent_category_id = vod["parent_category_id"]
		state = vod["state"]	#更新狀態
		last_fragment_symbol = vod["last_fragment_symbol"] #級數
		if parent_category_id in [101,102,103,105] :
			remarks = f"{state} {last_fragment_symbol}集"
		else:
			remarks = ""		
		return remarks

	#命名
	def getName(self):
		return "UBVod"
	
	
	def init(self,extend):
		if extend:
			data = json.loads(extend)
			self.siteUrl = data["url"]
			self.vip = data["vip"]
		else:
			self.siteUrl = "http://210.61.186.128:8989"

	
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
		video = []		
		video_list = []
		pagesize = 10
		if self.vip:
			pagesize = 40
			parent_category_ids = [108]
		else:		
			parent_category_ids = [100, 101, 102, 103]
		# 使用 ThreadPoolExecutor 進行並行請求
		with concurrent.futures.ThreadPoolExecutor() as executor:
			# 提交所有請求並創建 future-to-category 字典
			future_to_category = {
				executor.submit(self.fetch, f"{self.siteUrl}/api/video/recommend?parent_category_id={parent_category_id}&page=1&pagesize={pagesize}&kind=0"): 
				parent_category_id for parent_category_id in parent_category_ids
			}
			
			# 使用 as_completed 獲取所有完成的 future
			completed_futures = concurrent.futures.as_completed(future_to_category)
			for future in completed_futures:
				parent_category_id = future_to_category[future]
				try:
					response = future.result()
					data = response.json()				
					video_list.extend(data.get("video_hot_list", []))
				except Exception as ex:
					print(ex)

		# 構建最終的視頻列表
		for vod in video_list:
			video.append({
				"vod_id": vod["id"],
				"vod_name": vod["title"],
				"vod_pic": vod["pic"],
				"vod_remarks": self.vod_remark(vod)
			})
		
		result["list"] = video
	
		return result
		
	
	#分類頁
	def categoryContent(self, tid, pg, filter, extend):		
		result = {}	
		video = []			
		url = f"{self.siteUrl}/api/video/list"
		pagesize = 35
		
		params = {
			"parent_category_id": tid,
			"page": pg,
			"region": extend.get("region", ""),
			"year": extend.get("year", ""),
			"pagesize": pagesize			
		}
		
		try:
			response = self.fetch(url=url,params=params)
			data = response.json()
			video_list = data["data"]["video_list"]

			for vod in video_list:
				video.append({
					"vod_id": vod["id"],
					"vod_name": vod["title"],
					"vod_pic": vod["pic"],
					"vod_remarks": self.vod_remark(vod)
            	})

			result["list"] = video
			result["page"] = pg
			result["pagecount"] = 9999
			result["limit"] = pagesize
			result["total"] = 999999

		except Exception as ex:
			print(ex)
		
		return result 
	
	
	#搜索頁(舊)
	def searchContent(self, key, quick):
		return self.searchContentPage(key, quick, "1")
	
	
	#搜索頁(新)
	def searchContentPage(self, key, quick, pg):
		result = {}	
		video = []		
		pagesize = 35
		url = f"{self.siteUrl}/api/video/list"

		params = {
			"keyword": key,
			"page": 1,			
			"pagesize": pagesize			
		}
		try:
			response = self.fetch(url=url,params=params)
			data = response.json()
			video_list = data["data"]["video_list"]

			for vod in video_list:
				video.append({
					"vod_id": vod["id"],
					"vod_name": vod["title"],
					"vod_pic": vod["pic"],
					"vod_remarks": self.vod_remark(vod)
				})

			result["list"] = video

		except Exception as ex:
			print(ex)		
		
		return result
	
	
	#詳情頁
	def detailContent(self, ids):
		result = {}
		video = []
		video_id = ids[0]
		url = f"{self.siteUrl}/api/video/info?video_id={video_id}"

		try:
			response = self.fetch(url=url)
			data = response.json()
			data_video = data["video"]
			fragment_ids = data["video_fragment_list"]
			vod_play_urls  = ""
			for fragment_id in fragment_ids:
				vod_play_urls += f"{fragment_id['symbol']}${video_id}_{fragment_id['id']}#"

			video.append ({			
				"type_name": "",
				"vod_id": data_video.get("id", ""),
				"vod_name": data_video.get("title", ""),
				"vod_remarks": self.vod_remark(data_video),
				"vod_year": data_video.get("year", ""),
				"vod_area": data_video.get("region", ""),
				"vod_actor": data_video.get("starring", ""),
				"vod_director": data_video.get("director", ""),
				"vod_content":  data_video.get("description", ""),
				"vod_play_from": "安博",
				"vod_play_url": vod_play_urls.strip('#')
			})
			result['list'] = video
		
		except Exception as ex:
			print(ex)

		return result
	

	#播放頁
	def playerContent(self, flag, id, vipFlags):
		ids = id.split("_")
		video_id = ids[0]
		video_fragment_id = ids[1]
		url = f"{self.siteUrl}/api/video/source?video_id={video_id}&video_fragment_id={video_fragment_id}"

		try:
			response = self.fetch(url=url)
			data = response.json()		
			video_url = data["data"]["video_soruce"]["url"].split("?")[0] 
			result = {
				"parse": "0",
				"playUrl": "",
				"url": video_url,
				"header": ""
			} 

		except Exception as ex:
			print(ex)

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