# coding=utf-8
# !/usr/bin/python
import sys
sys.path.append('..')
from base.spider import Spider
import base64
from Crypto.Cipher import AES

class Spider(Spider):
    siteUrl = "https://www.czzy88.com"

    def getName(self):
        return "廠長"

    def init(self, extend=""):
        pass

    def homeContent(self,filter):
        result = {}
        cateManual = {
            "熱映中": "benyueremen",
            "電影": "zuixindianying",            
            "電視劇": "dsj",
            #"陸劇": "gcj",
            #"韓劇": "hanjutv",
            #"日劇": "riju",
            #"美劇": "meijutt",
            "動漫": "dm"
        }
        classes = []
        for k in cateManual:
            classes.append({
                'type_name': k,
                'type_id': cateManual[k]
            })
        result['class'] = classes
        return result

    def homeVideoContent(self):
        rsp = self.fetch(self.siteUrl)
        root = self.html(self.cleanText(rsp.text))
        vList = root.xpath("//div[@class='mi_btcon']//ul/li")
        vod = []
        for a in vList:
            name = a.xpath('./a/img/@alt')[0]
            pic = a.xpath('./a/img/@data-original')[0]             
            mark = (a.xpath("./div[@class='hdinfo']/span/text()") or [''])[0]
            sid = a.xpath("./a/@href")[0]
            sid = self.regStr(sid, "/movie/(\\S+).html")
            vod.append({
                "vod_id": sid,
                "vod_name": name,
                "vod_pic": pic,
                "vod_remarks": mark
            })
        return {'list': vod}

    def categoryContent(self, tid, pg, filter, extend):
        result = {}        
        url = f'{self.siteUrl}/{tid}/page/{pg}'
        rsp = self.fetch(url)
        root = self.html(self.cleanText(rsp.text))
        vList = root.xpath("//div[contains(@class,'mi_cont')]//ul/li")
        vod = []
        for v in vList:
            name = v.xpath('./a/img/@alt')[0]
            pic = v.xpath('./a/img/@data-original')[0]
            mark = (v.xpath("./div[@class='hdinfo']/span/text()") or [''])[0]
            sid = v.xpath("./a/@href")[0]
            sid = self.regStr(sid, "/movie/(\\S+).html")
            vod.append({
                "vod_id": sid,
                "vod_name": name,
                "vod_pic": pic,
                "vod_remarks": mark
            })

        result['list'] = vod
        result['page'] = pg
        result['pagecount'] = 9999
        result['limit'] = 90
        result['total'] = 999999
        return result    

    def detailContent(self, array):
        id = array[0]
        url = f'{self.siteUrl}/movie/{id}.html'
        rsp = self.fetch(url)
        root = self.html(self.cleanText(rsp.text))
        node = root.xpath("//div[@class='dyxingq']")[0]
        title = node.xpath('.//h1/text()')[0]
        pic = node.xpath(".//div[@class='dyimg fl']/img/@src")[0]     
        remarks = (node.xpath('.//li[contains(text(), "又名")]/a/text()') or [''])[0]
        year = (node.xpath('.//li[contains(text(), "年份")]/a/text()') or [''])[0]
        area = (node.xpath('.//li[contains(text(), "地区")]/a/text()') or [''])[0]
        typen = (node.xpath('.//li[contains(text(), "类型")]/a/text()') or [''])[0]
        actor = (node.xpath('.//li[contains(text(), "主演")]/span/text()') or [''])[0]
        director = (node.xpath('.//li[contains(text(), "导演")]/span/text()') or [''])[0]
        detail = (root.xpath(".//div[@class='yp_context']//p/text()") or [''])[0]        
        playUrls = []
        vList = root.xpath("//div[@class='paly_list_btn']")
        for v in vList:            
            aList = v.xpath('./a')
            for tA in aList:
                href = tA.xpath('./@href')[0]
                name = tA.xpath('./text()')[0]                
                url = self.regStr(href, '/v_play/(\\S+).html')
                playUrls.append(name + "$" + url)
        vod  = [{
            "vod_id": id,
            "vod_name": title,
            "vod_pic": pic,
            "type_name": typen,
            "vod_year": year,
            "vod_area": area,
            "vod_remarks": remarks,
            "vod_actor": actor,
            "vod_director": director,
            "vod_content": detail,
            'vod_play_from' : '廠長',
            "vod_play_url" : '#'.join(playUrls)
        }]
        return {'list': vod}

    def searchContent(self, key, quick):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Cookie": "cf_clearance=km3JnG5xXYksPTK9mj8NOcke_vdrsr7kMosxjCU5u.4-1703661075-0-2-3b2475e4.bc52cd1f.365a419b-150.0.0;"
        }
        url = f'{self.siteUrl}/xssearch?q={key}'        
        rsp = self.fetch(url,headers=headers)
        root = self.html(rsp.text)        
        vList = root.xpath("//div[contains(@class,'mi_ne_kd')]/ul/li/a")
        vod = []    
        
        for v in vList:
            name = v.xpath('./img/@alt')[0]
            pic = v.xpath('./img/@data-original')[0]
            href = v.xpath('./@href')[0]
            tid = self.regStr(href, 'movie/(\\S+).html')
            res = v.xpath('./div[@class="jidi"]/span/text()')
            if len(res) == 0:
                remark = '全1集'
            else:
                remark = v.xpath('./div[@class="jidi"]/span/text()')
            vod.append({
                    "vod_id": tid,
                    "vod_name": name,
                    "vod_pic": pic,
                    "vod_remarks": remark
            })                    
        return {'list': vod}
    
    def parseCBC(self, enc, key, iv):
        keyBytes = key.encode("utf-8")
        ivBytes = iv.encode("utf-8")
        cipher = AES.new(keyBytes, AES.MODE_CBC, ivBytes)
        msg = cipher.decrypt(enc)
        paddingLen = msg[len(msg) - 1]
        return msg[0:-paddingLen]

    def playerContent(self, flag, id, vipFlags):
        url = f'{self.siteUrl}/v_play/{id}.html'         
        pat = '\\"([^\\"]+)\\";var [\\d\\w]+=function dncry.*md5.enc.Utf8.parse\\(\\"([\\d\\w]+)\\".*md5.enc.Utf8.parse\\(([\\d]+)\\)'
        rsp = self.fetch(url)
        html = rsp.text        
        content = self.regStr(html, pat)        
        if content == '':
            return {}
        key = self.regStr(html, pat, 2)
        iv = self.regStr(html, pat, 3)
        print(f'key={key},iv={iv}')
        decontent = self.parseCBC(base64.b64decode(content), key, iv).decode()        
        urlPat = 'video: \\{url: \\\"([^\\\"]+)\\\"'
        vttPat = 'subtitle: \\{url:\\\"([^\\\"]+\\.vtt)\\\"'
        str3 = self.regStr(decontent, urlPat)
        str4 = self.regStr(decontent, vttPat)        
        self.loadVtt(str3)
        result = {
            'parse': '0',
            'playUrl': '',
            'url': str3,
            'header': ''
        }
        if len(str4) > 0:
            result['subf'] = '/vtt/utf-8'
            # result['subt'] = Proxy.localProxyUrl() + "?do=czspp&url=" + URLEncoder.encode(str4)
            result['subt'] = ''        
        return result

    def loadVtt(self, url):
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def localProxy(self, param):
        action = {}
        return [200, "video/MP2T", action, ""]