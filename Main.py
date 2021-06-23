#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#Reference: https://ithelp.ithome.com.tw/articles/10204709

import ssl
from urllib import request
from urllib import parse
from urllib.request import urlopen

import time
#import os
import pandas as pd
import csv
from datetime import datetime
import requests
from bs4 import BeautifulSoup
headers = {
    'Referer':'https://www.ptt.cc/',#如某些網站（如p站）要檢查referer，就給他加上
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'#每個爬蟲必備的偽裝
}

DuplicatedList = []

tmplist1 = [['Title','Author','Url','Time','Content','Push']]

PttStockCrawler_ID = "-1001379362917"
PTTCrawler_YO_ID = "-1001388313962"
groupID = [PttStockCrawler_ID, PTTCrawler_YO_ID]

TOPArticle = ["https://www.ptt.cc/bbs/Stock/M.1605850116.A.BDB.html", #[公告] Stock 股票板板規 V3.2 (2021/04/02修)
              "https://www.ptt.cc/bbs/Stock/M.1619866113.A.5C9.html", #[閒聊] 五月板務討論文 (周末可回文)
              "https://www.ptt.cc/bbs/Stock/M.1622042171.A.EB7.html"#, #[公告] 實習板主招募
              #"https://www.ptt.cc/bbs/Stock/M.1624255292.A.8D5.html"  #[閒沒] 2021/06/21 盤後閒聊
             ]

def SendMessageToTelegram(SendTitle, SendAuthorID, SendURL, SendGroupID):    
    teleText = SendTitle + "\n[Author]: " + SendAuthorID + "\n" + SendURL
    #print("SendtoTelegramGoup")
    #print(teleText)
    ssl._create_default_https_context = ssl._create_unverified_context
    values = {"method": "sendMessage", "chat_id":SendGroupID, "text":teleText}
    data = parse.urlencode(values).encode('utf-8')
    url = 'https://api.telegram.org/bot' + BOTToken_str + '/'
    #print(url)
    request1 = request.Request(url, data)
    response = urlopen(request1)
    #print(response.read().decode())
    time.sleep(0.5) # Delay for 0.5 seconds.

def CheckIDList(CheckTitle, CheckAuthorID, CheckURL):
    if CheckAuthorID in new_ID_List:
        if CheckDuplicatedList(CheckTitle+CheckAuthorID+CheckURL):
            for loopID in groupID:
                SendMessageToTelegram(CheckTitle, CheckAuthorID, CheckURL, loopID)
            DuplicatedList.append(CheckTitle+CheckAuthorID+CheckURL)
            
def CheckIDList_Push(CheckTitle, CheckAuthorID, CheckURL):
    #print(CheckAuthorID)
    if CheckAuthorID in new_ID_List:
        #print("Find" + CheckAuthorID)
        if CheckDuplicatedList(CheckTitle+CheckAuthorID+CheckURL):
            for loopID in groupID:
                SendMessageToTelegram(CheckTitle, CheckAuthorID, CheckURL, loopID)
            DuplicatedList.append(CheckTitle+CheckAuthorID+CheckURL)
            
def CheckTOPArticle(CheckURL):
    if CheckURL in TOPArticle:
        return 0
    else:
        return 1
    
def CheckDuplicatedList(DuplicatedText):
    if DuplicatedText in DuplicatedList:
        return 0
    else:
        return 1
            
def get_article_content(article_url):
    r = requests.get(article_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    results = soup.select("span.article-meta-value")
    content = soup.find(id="main-container")
    push  = soup.select("div.push")
    global tmplist
    if results:
        #print('作者:', results[0].text)
        #print('看板:', results[1].text)
        #print('標題:', results[2].text)
        #print('TIME:', results[3].text)
        tmplist.append(results[3].text)
    if content:
        #print('------------------ CONTENT ------------------')
        #print(content.text)
        tmplist.append(content.text)
    for item in push:
        author = item.select_one("span.push-userid")
        if author:
            author = author.text
            author = author.strip()
        push_content = item.select_one("span.push-content")
        if push_content:
            push_content = push_content.text
        push_time = item.select_one("span.push-ipdatetime")
        if push_time:
            push_time = push_time.text
            push_time = push_time.strip()
        if author and push_content and push_time:
            #print("-"+author+"-")
            #print(push_content)
            #print(push_time)
            tmplist.append(author + push_content + push_time)
            CheckIDList_Push("[推推推推推推推文!!!]\n"+ author + push_content + "\n[Time]: " + push_time, author, article_url)
            #print('標題:', push[2].text)
            #print('TIME:', push[3].text)
    tmplist1.append(tmplist)
    tmplist = []

def get_all_href(url):
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    results = soup.select("div.r-ent")
    #print(results)
    for item in results:
        a_item = item.select_one("a")
        if a_item:
            title = a_item.text
            author = item.select_one("div.author").text
            #print("="+author+"=")
            #print(title, author, 'https://www.ptt.cc'+ a_item.get('href'))
            if CheckTOPArticle('https://www.ptt.cc'+ a_item.get('href')):
                tmplist.append(title)
                tmplist.append(author)
                tmplist.append('https://www.ptt.cc'+ a_item.get('href'))
                
                CheckIDList("[發發發發發發發文!!!]\n" + title, author, 'https://www.ptt.cc'+ a_item.get('href'))
                get_article_content('https://www.ptt.cc'+a_item.get('href'))
                #print('------------------ NEXT ------------------')




                
                

print("PTTCrawler_YOLINYO_Bot_Version_1.1.3")
print("Start!")

print("Load ID_List.csv")
ID_List = pd.read_csv('ID_List.csv')
new_ID_List = list(ID_List['id'])

print("Load BOTToken.csv")
BOTToken = pd.read_csv('BOTToken.csv')
BOTToken_str = list(BOTToken)
BOTToken_str = BOTToken_str[0]

while 1:
    url="https://www.ptt.cc/bbs/Stock/index.html"
    tmplist = []
    now = datetime.now()
    dt_string = now.strftime("%Y%m%d-%H%M%S")
    print(dt_string)

    print("Page1...")
    get_all_href(url = url) #First page
    for page in range(1,5): #Previous page 2,3,4
        print("Page"+ str(page + 1) +"...")
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text,"html.parser")
        btn = soup.select('div.btn-group > a')
        if btn[3]['href']:
            up_page_href = btn[3]['href']
            next_page_url = 'https://www.ptt.cc' + up_page_href
            url = next_page_url
            get_all_href(url = url) #Previous page


    now = datetime.now()
    dt_string = now.strftime("%Y%m%d-%H%M%S")
    print(dt_string)
    kerker = open("./" + dt_string + ".csv","w",encoding="utf-8")#要用wb不可用w不然會每一行會多一行空白行
    print("Write Data into CSV file")
    w = csv.writer(kerker)
    w.writerows(tmplist1)
    kerker.close()
    print("Done!!")
    #os.system("pause")
    
    print("Sleep 15 mins...")

    time.sleep(900) # Delay for 120 seconds.


# In[ ]:




