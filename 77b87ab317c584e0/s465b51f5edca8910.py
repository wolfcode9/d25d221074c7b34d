#coding=utf-8
#!/usr/bin/python
import sys
sys.path.append('..') 
from s6ce0b3971a2f630d import Spider
import requests

class Spider(Spider):
	siteUrl = "https://www.yingshi.tv"

	def getName(self):
		return "影視"
	
	def init(self,extend=""):		
		self.extend = extend
	
	def homeContent(self,filter):
		result = {}				
		classes = [
			{"type_id": "2", "type_name": "電影"}, 
			{"type_id": "1", "type_name": "電視劇"},
			{"type_id": "3", "type_name": "綜藝"}, 
			{"type_id": "4", "type_name": "動漫" },
			{"type_id": "5", "type_name": "記錄片" }
		]
		result['class'] = classes
		if self.extend:			
			result['filters'] = self.fetch(self.extend).json()	
		return result
	
	def homeVideoContent(self):
		vod = []		
		rsp = self.fetch(self.siteUrl)
		root = self.html(rsp.text)								
		htmlData = root.xpath('//*[@id="desktop-container"]/section/div/div/li/a')       
		for h in htmlData:
			link = h.xpath("./@href")[0]
			vid = link.split('/')[4]
			name = (h.xpath('./h2[@class="ys_show_title"]/text()') or [None])[0]
			pic = (h.xpath('./div/img/@src') or [None])[0]
			mark = (h.xpath('.//span[@class="ys_show_episode_text"]/text()') or [None])[0] 
			if name:
				vod.append({"vod_id": vid, "vod_name": name,"vod_pic": pic,"vod_remarks": mark})
		
		'''
		#另一種很簡單的獲取json,直接取35筆(上限)
		url = f'{self.siteUrl}/ajax/data.html?mid=1&limit=35&by=score&order=desc'		
		vodData = self.fetch(url).json()
		'''					
		return {'list': vod}

	def categoryContent(self,tid,pg,filter,extend):
		#url = f'{self.siteUrl}/ajax/data?mid=1&page={pg}&limit=35&tid={tid}&by=time'		
		result = {}	
		params = {
			"tid": tid,
			"page": pg,
			"limit": "35",
			"mid": "1",
			"by": "time",
			"class": extend.get("class", ""),
			"year": extend.get("year", ""),
			"lang": extend.get("lang", ""),
			"area": extend.get("area", "")			
		}
		url = f'{self.siteUrl}/ajax/data'		
		rsp = requests.get(url=url,params=params)
		if rsp.text:
			vod = []
			jsonData = rsp.json()
			for v in jsonData['list']:
				vod.append({
					"vod_id": v['vod_id'],
					"vod_name": v['vod_name'],
					"vod_pic": v['vod_pic'],
					"vod_remarks": v['vod_remarks']
            	})			
			result['list'] = vod
			result['page'] = pg
			result['pagecount'] = jsonData['pagecount']
			result['limit'] = 35
			result['total'] = jsonData['total']
		return result 
	
	def detailContent(self,array):
		result = {}
		tid = array[0]
		url = f"{self.siteUrl}/vod/play/id/{tid}/sid/1/nid/1.html"
		rsp = self.fetch(url)		
		root = self.html(rsp.text)
		htmlData = root.xpath('//script[contains(text(), "let data = ") and contains(text(), "let obj = ")]/text()')[0]
		vod = self.str2json(htmlData.split('let data = ')[1].split('let obj = ')[0].strip()[:-1].replace("&amp;", " "))
		result = {'list': [{
			"vod_id": vod['vod_id'],
			"vod_name": vod['vod_name'],
			"vod_pic": vod['vod_pic'],
			"vod_remarks": vod['vod_remarks'],
			"type_name": vod['type']['type_name'],
			"vod_year": vod['vod_year'],
			"vod_area": vod['vod_area'],
			"vod_actor": vod['vod_actor'],
			"vod_director": vod['vod_director'],
			"vod_content": vod['vod_content'],
			"vod_play_from": "✡️", #vod['vod_play_from'],
			"vod_play_url": vod['vod_play_url']
		}]}			
		return result
	
	def searchContent(self,key,quick):		
		url = f'{self.siteUrl}/ajax/search.html?wd={key}&mid=1&limit=18&page=1'		
		jsonData = self.fetch(url).json()['list'][0]		
		result = {'list': [{
			"vod_id": jsonData['vod_id'],
			"vod_name": jsonData['vod_name'],
			"vod_pic": jsonData['vod_pic'],
			"vod_remarks": jsonData['vod_remarks']
		}]}
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