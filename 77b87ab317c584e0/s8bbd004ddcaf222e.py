o
    �$�f|  �                   @   sL   d dl Z e j�d� d dlmZ d dlZd dlZd dlZG dd� de�ZdS )�    Nz..)�Spiderc                   @   s*  e Zd ZdZdZded�Zej�� jZ	dd� e
e	e	d d�D �Zi d	d
ddd�ddd�ddd�ddd�ddd�ddd�ddd�ddd�ddd�g	d�ddddd�ge�d�gd�Zi fdd�Zdd� Zdd� Zdd � Zd!d"� Zd#d$� Zd%d&� Zd'd(� Zd)d*� Zd+d,� Zd-d.� Zd/d0� Zd1d2� Zd3d4� Zd5S )6r   � r   zoMozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36)z
user-agentZRefererc                 C   s   g | ]	}|� |� d ��qS )��n�v� )�.0�yearr   r   �s8bbd004ddcaf222e.py�
<listcomp>   s    zSpider.<listcomp>�   ������regionu   地區u   全部r   u   大陸u   歐美u   日本u   臺灣u   香港u   韓國u	   新馬泰u   其他)�key�name�valuer	   u   年份)Zplayer�filterc                 C   s<   |d }|d }|d }|dv r|� d|� d�}|S d}|S )N�parent_category_id�state�last_fragment_symbol)�e   �f   �g   �i   � u   集r   r   )�self�vodr   r   r   Zremarksr   r   r
   �
vod_remark-   s   �zSpider.vod_remarkc                 C   s   dS )NZUBVodr   �r   r   r   r
   �getName8   �   zSpider.getNamec                 C   s2   zt �|�}|d | _|d | _W d S    Y d S )N�url�vip)�json�loads�siteUrlr"   )r   �extend�datar   r   r
   �init<   s   

zSpider.initc                    s\   � j r
ddd�g}nddd�ddd�dd	d�d
dd�ddd�g}� fdd�|D �|d�}|S )NZ108u   成人)�type_id�	type_nameZ100u   電影Z101u	   電視劇Z102u   綜藝Z103u   動漫Z105u   紀實c                    s   i | ]
}|d  � j d �qS )r)   r   )�config)r   �itemr   r   r
   �
<dictcomp>S   s    z&Spider.homeContent.<locals>.<dictcomp>)�filters�class)r"   )r   r   Zclasses�resultr   r   r
   �homeContentF   s   �zSpider.homeContentc                    s8  i }g }g }d� �j rd�dg}nd�g d�}tj�� �Z�� ���fdd�|D �}tj�|�}|D ]=}|| }z!|�� }	|	�� }
� dkrN|�|
�d	g �� n	|�|
�d
g �� W q1 t	yn } z
t
|� W Y d }~q1d }~ww W d   � n1 syw   Y  |D ]}|�|d |d |d ��|�d�� q�||d< |S )N�   �d   �l   �
   )r3   r   r   r   c                    s4   i | ]}�� �j�j� d |� d�� d� � ��|�qS )z(/api/video/recommend?parent_category_id=z&page=1&pagesize=z&by=)Zsubmit�fetchr%   )r   r   �ZbyZexecutor�pagesizer   r   r
   r-   j   s
    $��z+Spider.homeVideoContent.<locals>.<dictcomp>r   Zvideo_hot_listZvideo_latest_list�id�title�pic��vod_id�vod_nameZvod_pic�vod_remarks�list)r"   �
concurrentZfuturesZThreadPoolExecutorZas_completedr0   r#   r&   �get�	Exception�print�appendr   )r   r0   �video�
video_listZparent_category_idsZfuture_to_categoryZcompleted_futuresZfuturer   �responser'   �exr   r   r7   r
   �homeVideoContentX   sL   ������
�zSpider.homeVideoContentc              
   C   s�   i }g }| j � d�}d}|||�dd�|�dd�|d�}	z@| j||	d�}
|
�� }|d d	 }|D ]}|�|d
 |d |d | �|�d�� q0||d< ||d< d|d< ||d< d|d< W |S  tys } zt|� W Y d }~|S d }~ww )N�/api/video/list�   r   r   r	   )r   �pager   r	   r8   �r!   �paramsr'   rG   r9   r:   r;   r<   r@   rM   i'  Z	pagecount�limiti?B �total)r%   rB   r6   r#   rE   r   rC   rD   )r   �tid�pgr   r&   r0   rF   r!   r8   rO   rH   r'   rG   r   rI   r   r   r
   �categoryContent�   s@   

�
�
���zSpider.categoryContentc                 C   s   | � ||d�S )N�1)�searchContentPage)r   r   �quickr   r   r
   �searchContent�   s   zSpider.searchContentc              
   C   s�   i }g }d}| j � d�}|d|d�}z0| j||d�}	|	�� }
|
d d }|D ]}|�|d |d	 |d
 | �|�d�� q&||d< W |S  tyY } zt|� W Y d }~|S d }~ww )N�#   rK   �   )�keywordrM   r8   rN   r'   rG   r9   r:   r;   r<   r@   )r%   r6   r#   rE   r   rC   rD   )r   r   rW   rS   r0   rF   r8   r!   rO   rH   r'   rG   r   rI   r   r   r
   rV   �   s4   �
�
���zSpider.searchContentPagec                 C   s  i }g }|d }| j � d|� �}zd| j|d�}|�� }|d }|d }	d}
|	D ]}|
|d � d|� d	|d
 � d�7 }
q'|�d|�d
d�|�dd�| �|�|�dd�|�dd�|�dd�|�dd�|�dd�d|
�d�d�� ||d< W |S  ty� } zt|� W Y d }~|S d }~ww )Nr   z/api/video/info?video_id=�r!   rF   Zvideo_fragment_listr   �symbol�$�_r9   �#r:   r	   r   ZstarringZdirector�descriptionu   安博)r*   r=   r>   r?   Zvod_yearZvod_areaZ	vod_actorZvod_directorZvod_contentZvod_play_fromZvod_play_urlr@   )	r%   r6   r#   rE   rB   r   �striprC   rD   )r   �idsr0   rF   �video_idr!   rH   r'   Z
data_videoZfragment_idsZvod_play_urlsZfragment_idrI   r   r   r
   �detailContent�   s@   $






�
���zSpider.detailContentc              
   C   s�   |� d�}|d }|d }| j� d|� d|� �}z!| j|d�}|�� }	|	d d d	 � d
�d }
dd|
dd�}W |S  tyP } zt|� W Y d }~|S d }~ww )Nr_   r   rZ   z/api/video/source?video_id=z&video_fragment_id=r\   r'   Zvideo_sorucer!   �?�0r   )�parseZplayUrlr!   �header)�splitr%   r6   r#   rC   rD   )r   �flagr9   ZvipFlagsrc   rd   Zvideo_fragment_idr!   rH   r'   Z	video_urlr0   rI   r   r   r
   �playerContent  s&   
�
���zSpider.playerContentc                 C   �   d S �Nr   r   r   r   r
   �destroy  r    zSpider.destroyc                 C   rm   rn   r   )r   r!   r   r   r
   �isVideoFormat  r    zSpider.isVideoFormatc                 C   rm   rn   r   r   r   r   r
   �manualVideoCheck#  r    zSpider.manualVideoCheckc                 C   s   dddddd�}dd|dgS )Nr   �string)r!   ri   �param�typeZafter��   z
video/MP2Tr   )r   rs   �actionr   r   r
   �
localProxy(  s   �zSpider.localProxyN)�__name__�
__module__�__qualname__r%   r"   ri   �datetimeZnowr	   Zcurrent_year�rangeZyearsr+   r   r   r(   r1   rJ   rT   rX   rV   re   rl   ro   rp   rq   rw   r   r   r   r
   r   
   sR    ������
6(!%r   )	�sys�pathrE   Zbase.spiderr   Zconcurrent.futuresrA   r{   r#   r   r   r   r
   �<module>   s   