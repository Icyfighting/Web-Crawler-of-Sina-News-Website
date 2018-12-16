#!/usr/bin/env python
# coding: utf-8

# In[1]:


commentCountUrl = 'https://comment5.news.sina.com.cn/cmnt/count?format=json&newslist=gn:comos-{}:0'
commentCountUrl2 = 'https://comment.sina.com.cn/page/info?version=1&format=json&channel=cj&newsid=comos-{}'
import re
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
def getCommentCount(newsurl):
    m = re.search('doc-i(.+).shtml',newsurl)  #根据新闻url找出新闻的id
    newsid= m.group(1)
   # print(newsid)
    commentCountUrlFormat = commentCountUrl.format(newsid)   #根据新闻id，组合出评论数量的链接
    commentCountUrlFormat2 = commentCountUrl2.format(newsid)
    #根据评论数量链接，取得评论数
    res = requests.get(commentCountUrlFormat)
    res2 = requests.get(commentCountUrlFormat2)
    res.encoding='utf-8'
   # print(res.text)
    mm = re.search('\"total\":.*?(?=,)',res.text)
    mm2 = re.search('\"total\":.*?(?=,)',res2.text) #这两个路径中只有一个是有返回值的，另一个没有返回值，需要判断
    commentCount1=0
    commentCount2=0
    if mm is not None:
        commentCountStr1 = mm.group(0).lstrip('"total":').strip()
        commentCount1 = int(commentCountStr1)
    if mm2 is not None:
        commentCountStr2 = mm2.group(0).lstrip('"total":').strip()
        commentCount2 = int(commentCountStr2)
    
    #当第二个地址返回正确 ，但是第一个地址返回也不是空，知识内容是0，所以不为空的都要取，然后返回大的评论数
    
    
    if commentCount1 > commentCount2:
        return commentCount1
    else:
        return commentCount2
  


# In[2]:


def getAuthor(soup):
    
    show_author = soup.select('.show_author')
    article_editor = soup.select('.article-editor')
    if len(show_author)>0:
        return show_author[0].text.lstrip('责任编辑：') 
    elif len(article_editor)>0:
        return article_editor[0].text.lstrip('责任编辑：')
    else:
        return 'null'


# In[3]:


def getNewsDetail(newsurl):
    result = {}
    res = requests.get(newsurl)
    res.encoding='utf-8'
    soup = BeautifulSoup(res.text,'html.parser')
    result['title'] = soup.select('.main-title')[0].text
    result['dt'] = datetime.strptime(soup.select('.date')[0].text,'%Y年%m月%d日 %H:%M')
    result['newssource'] = soup.select('.source')[0].text
    result['article'] = ' '.join([p.text.strip() for p in soup.select('.article p')[:-1]])
    result['editor'] = getAuthor(soup)
    result['commentsCount'] = getCommentCount(newsurl)
    return result


# In[4]:


def parseListLinks(pageUrl):
    newsdetails = []
    res = requests.get(pageUrl)
    res.encoding='utf-8'
    jd = json.loads(res.text)
    for ent in jd['result']['data']:
        newsdetails.append(getNewsDetail(ent['url']))
    return newsdetails


# In[5]:


def getNewsTotal(start, end):
    pageCommonUrl = 'https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2509&k=&num=10&page={}'
    if str(start).isdigit() and str(end).isdigit():
        if int(start)< int(end):
            news_total = []
            for i in range(int(start),int(end)):
                newsurl = pageCommonUrl.format(i)
                newsary = parseListLinks(newsurl)
                news_total.extend(newsary)
            return news_total
        else:
            return None
    else:
        return None
    


# In[6]:


import pandas
df = pandas.DataFrame(getNewsTotal(11,13))
df.head(20)


# In[7]:


df.to_excel('news_result.xlsx')

