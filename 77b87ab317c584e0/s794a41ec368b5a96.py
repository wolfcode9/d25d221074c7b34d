#coding=utf-8
#!/usr/bin/python
import sys
sys.path.append('..') 
from base.spider import Spider
import requests
import re
import json
from datetime import datetime

current_year = datetime.now().year

# Generate years from current year to 12 years ago
years = [{"n": str(year), "v": str(year)} for year in range(current_year, current_year - 13, -1)]
years.insert(0, {"n": "全部", "v": ""})

# Define categories
categories = {
    "1": [
        {"n": "全部", "v": ""},
        {"n": "动作片", "v": "6"},
        {"n": "喜剧片", "v": "7"},
        {"n": "爱情片", "v": "8"},
        {"n": "科幻片", "v": "9"},
        {"n": "恐怖片", "v": "10"},
        {"n": "剧情片", "v": "11"},
        {"n": "战争片", "v": "12"},
        {"n": "记录片", "v": "20"}
    ],
    "2": [
        {"n": "全部", "v": ""},
        {"n": "大陆", "v": "13"},
        {"n": "台湾", "v": "21"},
        {"n": "韩国", "v": "15"},
        {"n": "日本", "v": "22"},
        {"n": "欧美", "v": "16"}
    ],
    "3": [
        {"n": "全部", "v": ""},
        {"n": "大陆", "v": "25"},
        {"n": "台湾", "v": "26"},
        {"n": "日韩", "v": "27"},
        {"n": "欧美", "v": "28"}
    ],
    "4": [
        {"n": "全部", "v": ""},
        {"n": "大陆", "v": "29"},
        {"n": "日韩", "v": "30"},
        {"n": "台湾", "v": "32"},
        {"n": "欧美", "v": "31"}
    ]
}

filters = {key: [{"key": "Category", "name": "类型", "value": value}, {"key": "Year", "name": "年份", "value": years}] for key, value in categories.items()}

class Spider(Spider):	
	siteUrl = "https://m.mubai.link"		

	def getName(self):
		return "慕白"
	
	def init(self,extend):
		self.extend = extend
		
	def homeContent(self,filter):		
		result = {}
		classes = [
			{"type_id": "1", "type_name": "電影"}, 
			{"type_id": "2", "type_name": "電視劇"},
			{"type_id": "3", "type_name": "綜藝"}, 
			{"type_id": "4", "type_name": "動漫" }
		]
		result['class'] = classes
		result['filters'] = filters
		return result
	
	def homeVideoContent(self):		
		result = {}
		url = f'{self.siteUrl}/api/index'
		rsp = self.fetch(url)	
		vod = []
		jsonData = rsp.json()
		for content in jsonData['data']['content']:
			for v in content['movies']:
				vod.append({
					"vod_id": v['id'],
					"vod_name": v['name'],
					"vod_pic": v['picture'],
					"vod_remarks": v['remarks']
				})
		result['list'] = vod
		return result
	
	def categoryContent(self,tid,pg,filter,extend):
		#https://m.mubai.link/filmClassifySearch?Pid=1&Sort=release_stamp&current=1
		result = {}	
		vod = []			
		params = {
			"Pid": tid,
			"current": pg,
			"Sort": extend.get("Sort", "release_stamp"),
			"Category": extend.get("Category", ""),
			"Plot": extend.get("Plot", ""),			
			"Year": extend.get("Year", ""),
			"Language": extend.get("Language", ""),
			"Area": extend.get("Area", "")
		}
		url = f'{self.siteUrl}/api/filmClassifySearch'
		rsp = requests.get(url=url,params=params)

		if rsp.text:
			jsonData = rsp.json()
			for v in jsonData['data']['list']:
				vod.append({
					"vod_id": v['id'],
					"vod_name": v['name'],
					"vod_pic": v['picture'],
					"vod_remarks": v['remarks']
            	})
			result['list'] = vod
			result['page'] = pg
			result['pagecount'] = jsonData['page']['pageCount']
			result['limit'] = 35
			result['total'] = jsonData['page']['total']
		return result 
	
	def detailContent(self, ids):
		#https://m.mubai.link/api/filmDetail?id=77886
		result = {}		
		id = ids[0]
		url = f"{self.siteUrl}/api/filmDetail?id={id}"
		rsp = self.fetch(url)
		if rsp.text:
			playUrls = []			
			vod = []
			jsonData = rsp.json()
			jsonData = jsonData['data']['detail']			
			for v in jsonData['playList'][0]:				
				playUrls.append('#'.join([v['episode'] + '$' + v['link']]))
			cleaned_content = re.sub(r'<p>\s*|\s*</p>', '', jsonData['descriptor']['content'])			
			vod.append ({
				"vod_id": id,
				"vod_name": jsonData['name'],
				"vod_pic":  jsonData['picture'],
				"type_name": jsonData['descriptor']['classTag'],
				"vod_remarks": jsonData['descriptor']['remarks'],
				"vod_year": jsonData['descriptor']['year'],
				"vod_area": jsonData['descriptor']['area'],
				"vod_actor": jsonData['descriptor']['actor'],
				"vod_director": jsonData['descriptor']['director'],
				"vod_content": cleaned_content,
				"vod_play_from" : '✡️',
				"vod_play_url" : '#'.join(playUrls)
				})			
			result['list'] = vod
		return result	
	 
	def searchContent(self,key,quick):
		#https://m.mubai.link/search?search=我知道我爱你
		result = {}
		url = f'{self.siteUrl}/api/searchFilm?keyword={key}'
		rsp = self.fetch(url)		
		vod = []
		jsonData = rsp.json()
		jsonData = jsonData['data']['list']
		for v in jsonData:
			vod.append({
				"vod_id": v['id'],
				"vod_name": v['name'],
				"vod_pic": v['picture'],
				"vod_remarks": v['remarks']
			})      
		result['list'] = vod
		return result
	
	def searchContentPage(self, key, quick, pg):
		pass

	def searchContentPage(self, key, quick, pg):
		pass

	def playerContent(self,flag,id,vipFlags):
		result = {
        	'parse': '0',
            'playUrl': '',
            'url': id,
            'header': ''
        }
		return result
	
	def destroy(self):
		pass

	def isVideoFormat(self,url):
		pass
	
	def manualVideoCheck(self):
		pass
	
	def localProxy(self,param):
		action = {
			'url':'',
			'header':'',
			'param':'',
			'type':'string',
			'after':''
		}
		return [200, "video/MP2T", action, ""]