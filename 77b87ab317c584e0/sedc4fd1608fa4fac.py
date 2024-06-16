#coding=utf-8
#!/usr/bin/python
import sys
sys.path.append('..') 
from base.spider import Spider
import concurrent.futures

class Spider(Spider):	
	
	def getName(self):
		return "豆瓣薦片"
	
	def init(self,extend=""):
		pass	
	
	def homeContent(self,filter=None):				
		classes = [
			{"type_id": "movie", "type_name": "熱播電影"}, 
			{"type_id": "tv", "type_name": "熱播劇集"}
		]
		return {'class': classes}
	
	def homeVideoContent(self):
		limit = 10
		#電視劇 https://movie.douban.com/j/search_subjects?type=tv&tag=热门&page_limit=50&page_start=0
		#電影 https://movie.douban.com/j/search_subjects?type=movie&tag=热门&page_limit=50&page_start=0
		with concurrent.futures.ThreadPoolExecutor() as executor:					
			j_movie = executor.submit(self.fetch_vodData,self.douban_url('movie',limit,0)).result()
			j_tv = executor.submit(self.fetch_vodData,self.douban_url('tv',limit,0)).result()			
		return  {'list': (j_tv + j_movie)}
	
	def categoryContent(self,tid,pg,filter,extend):	
		result = {}		
		start = (int(pg) - 1) * 20		
		limit = 50
		total = 1000
		pagecount = int(total/limit)
		result['list'] = self.fetch_vodData(self.douban_url(tid,limit,start))
		result['limit'] = limit
		result['page'] = pg
		result['pagecount'] = pagecount
		result['total'] = total
		return result
	
	def detailContent(self,array):
		result = {}
		return result
	
	def searchContent(self,key,quick):
		result = {}
		return result
	
	def playerContent(self,flag,id,vipFlags):
		result = {}
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
	
	def douban_url(self,typeid,limit,pg):
		return f'https://movie.douban.com/j/search_subjects?type={typeid}&tag=热门&page_limit={limit}&page_start={pg}'

	def fetch_vodData(self,url):
		vod = []
		header = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
		jsonData = self.fetch(url=url,headers=header).json()		
		for v in jsonData['subjects']:
			remarks = v['episodes_info'] or v['rate']
			vod.append({				
				"vod_id": '',
				"vod_name": v['title'],
				"vod_pic": v['cover'],
				"vod_remarks": remarks
			})
		return vod