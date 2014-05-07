__author__ = 'cboys'

from bs4 import BeautifulSoup
import requests
import re
import math
import os
import time
import json
import mandrill
import smtplib
import threading
import cPickle as pickle

scrapings_dir='scrapings'
if not os.path.exists(scrapings_dir):
        os.mkdir(scrapings_dir)
#mandrill_client=mandrill.Mandrill(dZkyaV369DEIq05GtvpCJw)

artist="arctic monkeys"
city="sydney"
URL_START='http://www.gumtree.com.au'
OFFER_CHOICE=['k0?ad=offering','k0?ad=wanted']
ARTIST_URL="arctic+monkeys"#re.sub("\s",+,artist)

def scrape_gumtree():
    current_time=int(time.time())
    pageURL='{0}/s-{1}+{2}/{3}'.format(URL_START,ARTIST_URL,city,OFFER_CHOICE)
    savePath=os.path.join(scrapings_dir,"{0}.html".format(current_time))
    results=requests.get(pageURL)
    results_file=open(savePath,'w')
    with results_file:
        results_file.write(results.text.encode('utf-8',errors='ignore'))
    return savePath

def html_parser(filename):
    gumtree_file=open(filename)
    gumtree_contents=gumtree_file.read()
    gtsoup=BeautifulSoup(gumtree_contents)
    master_list=[]
    gt_li=gtsoup.findAll('li', attrs={'class': 'js-click-block'})
    for node in gt_li:
        if len(node.contents) > 0:
            post_dict={}
            if node.findAll('a') is not None:
                post_dict['title']=node.findAll('a')[0].string
            if node.find('div',attrs={"class":"h-elips"}) is not None:
                post_dict['price']=node.find('div',attrs={"class":"h-elips"}).string
            if node.findAll('span') is not None:
                post_dict['description']=node.findAll('span')[0].contents[0]
            if node.find('h3',attrs={"class":"rs-ad-location"}) is not None:
                post_dict['location1']=node.find('h3',attrs={"class":"rs-ad-location-area"}).contents[0]
            if node.find('span',attrs={"class":"rs-ad-location-suburb"}) is not None:
                post_dict['location2']=node.find('span',attrs={"class":"rs-ad-location-suburb"}).contents[0]
            if node.find('div',attrs={"class":"rs-ad-date"}) is not None:
                post_dict['date']=node.find('div',attrs={"class":"rs-ad-date"}).contents[0]
            anchors=node.findAll('a')
            for node in anchors:
                if node.get("data-adid") is not None:
                    post_dict['ad_id']=node.get('data-adid')
            master_list.append(post_dict)
    return master_list

#with open('master_list.txt',"a+") as master_file:
#    current_scrape=html_parser(scrape_gumtree())

#parsedPath=os.path.join(scrapings_dir,"{0}.text".format(int(time.time())))

def regular_scraping():
    json_file=open('master_file.text',"r")
    json_file_contents= json_file.read()
    if not os.stat('master_file.text')[6]==0:
        old_data=json.loads(json_file_contents)
    else:
        old_data=[]
    print type(old_data)
    this_scrape=html_parser(scrape_gumtree())
    data_ids=[]
    new_entries=[]
    new_entry_count=0
    for entry in old_data:
        data_ids.append(entry[u'ad_id'])
 #   print data_ids
    for entry in this_scrape:
#        print (entry,"\n")
        if entry[u'ad_id'] not in data_ids:
            old_data.append(entry)
            new_entry_count += 1
            new_entries.append(entry)
    json_file.close()
    json_file=open('master_file.text',"w")
    json_file.write(json.dumps(old_data))
    json_file.close()
#    threading.Timer(60, regular_scraping()).start()

regular_scraping()

#print len(html_parser(scrape_gumtree()))