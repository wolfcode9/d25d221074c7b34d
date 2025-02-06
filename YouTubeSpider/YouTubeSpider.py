### YouTube直播頻道爬蟲
### Updated 2025-02-03 By WolfCode.

import requests
import json
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
from tqdm import tqdm
import logging
from pathlib import Path


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class YouTubeSpider():
    def __init__(self,config_path:str = None):        
        self.config_path = config_path or Path(__file__).parent / "source.json"
        self.target_channels = []        
        self.session = requests.Session()
        self.load_config()

        
    def session_get(self, url:str, timeout=10) -> requests.Response:
        return self.session.get(url, headers=
        {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/321 (KHTML, like Gecko) Chrome/62.0.3202.9 Safari/537.36',},
        timeout=timeout
        )

    
    def load_config(self) -> None:
        """載入目標頻道設定"""        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.target_channels = json.load(f)
        except Exception as e:
            logging.error(f"Failed to load config: {e}")
            self.target_channels = []

                    
    def fetch_ytInitialData(self, url:str)-> dict:
        """獲取 ytInitialData 資料並解析JSON"""                    
        response = self.session_get(url)
        pattern = r'(?:window\["ytInitialData"\]|var ytInitialData)\s*=\s*(\{.*?\});'        
        match = re.search(pattern, response.text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        else:
            logging.error(f"Failed to fetch, {url}")                
                
    
    def get_play_urls(self,channels={}, workers=5)->list:
        """併發獲取播放URL"""
        result = []        
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(self.get_info_by_username, channel) for channel in channels]            
            with tqdm(total=len(channels), desc="YouTube - Fetching Play URIs") as pbar:
                for future in as_completed(futures):              
                    result.append({"channelName": channels[futures.index(future)]["channelName"], "playUri": future.result()})
                    pbar.update(1)        
        return result

    
    def get_info_by_username(self, channel)->list:
        """獲取頻道影片資訊"""
        try:            
            ytInitialData = self.fetch_ytInitialData(channel["source"])
            # 提取視頻標題和標籤
            title = ytInitialData["microformat"]["microformatDataRenderer"]["title"]
            tabs = ytInitialData["contents"]["twoColumnBrowseResultsRenderer"]["tabs"]
        except:             
            return []

        vodInfo = []
        for tab in tabs:
            if tab.get("tabRenderer", {}).get("title") not in {"直播", "影片"}:    
                continue  # 跳過不匹配的標籤            
            
            tab_contents = tab["tabRenderer"].get("content", {}).get("richGridRenderer", {}).get("contents", [])      

            for item in tab_contents:
                video_renderer = item.get("richItemRenderer", {}).get("content", {}).get("videoRenderer")                    
                if not video_renderer:
                    continue  # 跳過無效的條目

                videoId = video_renderer.get("videoId")
                viewCountText = video_renderer.get("viewCountText", {})
                username = re.search("@(.*?)/", channel["source"])[1].replace("/", "")
                videoName = video_renderer["title"]["runs"][0]["text"]
                watchUrl = f'https://www.youtube.com/watch?v={videoId}'
                imgUrl = f'https://i.ytimg.com/vi/{videoId}/hqdefault.jpg'
                liveNow = bool(viewCountText.get("runs", [{}])[0].get("text",False)) 
                liveCount = int(re.sub(r'\D', '', viewCountText["runs"][0]["text"])) if "runs" in viewCountText else 0
                viewCount = int(re.sub(r'\D', '', viewCountText["simpleText"])) if "simpleText" in viewCountText else 0
                vodInfo.append({
                    "supplier":"YouTube",
                    "group": channel["group"],                                
                    "channelName": channel["channelName"],
                    "username": username,
                    "title": title,
                    "videoId": videoId,
                    "videoName": videoName,
                    "liveNow": liveNow,
                    "liveCount": liveCount,
                    "viewCount": viewCount,
                    "watchUrl": watchUrl,
                    "imgUrl": imgUrl
                })                
                   
        # 按 liveCount 排序
        vodInfo = sorted(vodInfo, key=lambda x: x['liveCount'], reverse=True)
        return vodInfo

    
    def search(self, keyword, liveNow=False)->list:
        """搜尋影片(20部影片)"""
        try:
            sp = "EgQQAUAB" if liveNow else "CAISAhAB"
            ytInitialData = self.fetch_ytInitialData(f"https://www.youtube.com/results?search_query={keyword}&sp={sp}")            
            sections = ytInitialData["contents"]["twoColumnSearchResultsRenderer"]["primaryContents"]["sectionListRenderer"]["contents"]              
        except:
            return []

        vodInfo = []
        for item in sections:
            if item.get("itemSectionRenderer"):
                for contents in item["itemSectionRenderer"]["contents"]:
                    if contents.get("videoRenderer"):                                        
                        videoName = contents["videoRenderer"]["title"]["runs"][0]["text"]
                        videoId = contents["videoRenderer"]["videoId"]
                        watchUrl = f'https://www.youtube.com/watch?v={videoId}'
                        imgUrl = f'https://i.ytimg.com/vi/{videoId}/hqdefault.jpg'                            
                        viewCountText = contents["videoRenderer"].get("viewCountText", {})
                        liveNow = bool(viewCountText.get("runs", [{}])[0].get("text", False))                        
                        liveCount = int(re.sub(r'\D', '', viewCountText.get("runs", [{}])[0].get("text", "0"))) if "runs" in viewCountText else 0
                        viewCount = int(re.sub(r'\D', '', viewCountText.get("simpleText", "0"))) if "simpleText" in viewCountText else 0
                        if liveNow == False or (liveNow == True and liveNow == True):
                            vodInfo.append({ "supplier":"YouTube","channelName":videoName,"watchUrl":watchUrl,"imgUrl":imgUrl,"liveNow":liveNow, "viewCount":viewCount, "liveCount":liveCount})
        vodInfo = sorted(vodInfo, key=lambda x: x['viewCount'], reverse=True)
        return vodInfo        

    
    def run_spider(self):
        """執行爬蟲"""
        logging.info("Starting YouTube spider...")
        playInfo = []
        PlayUrls = self.get_play_urls(channels=self.target_channels)
        for channel in self.target_channels: 
            channel["Found"] = False
            for X in PlayUrls:
                for x in X["playUri"]:                       
                    if x["channelName"] == channel["channelName"] and x["liveNow"] == True and (channel["query"] in x["videoName"] or channel["query"] == ""):
                        playInfo.append(x)                      
                        channel["Found"] = True
                        break
        for channel in self.target_channels:
            if channel.get("Found") == False:
                logging.warning(f'Not Found: {channel["channelName"]} ({channel["source"]},{channel["query"]})')
        return playInfo


if __name__ == "__main__":    
    #sp = YouTubeSpider()   
    #print(sp.run_spider())
    #print(sp.search("音樂",1))
    pass