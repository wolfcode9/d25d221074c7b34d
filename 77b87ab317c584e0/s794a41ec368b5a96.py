#coding=utf-8
#!/usr/bin/python
import sys
from s6ce0b3971a2f630d import Spider
import requests
import re

class Spider(Spider):	
	siteUrl = "https://m.mubai.link"

	def getName(self):
		return "慕白"
	
	def init(self,extend=""):
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
		if self.extend:			
			result['filters'] =  self.fetch(self.extend).json()
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
	
	def detailContent(self,array):
		#https://m.mubai.link/api/filmDetail?id=77886
		result = {}		
		id = array[0]
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
	
	def playerContent(self,flag,id,vipFlags):
		result = {
        	'parse': '0',
            'playUrl': '',
            'url': id,
            'header': ''
        }
		return result
	
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