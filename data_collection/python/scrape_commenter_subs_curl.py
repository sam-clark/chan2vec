import sys
import os
import time
import random
import datetime
import json
import subprocess

#import requests
#from bs4 import BeautifulSoup

import scrape_email_util

def expand_num(sub_raw):
    if sub_raw[-1] == "M":
        sub_c = float(sub_raw[:-1])*1000000
    elif sub_raw[-1] == "K":
        sub_c = float(sub_raw[:-1])*1000
    else:
        sub_c = float(sub_raw)
    return sub_c


def scrape_subscriptions(html):
    """
    soup = BeautifulSoup(html, 'html.parser')
    sub_l = []
    for chan_sub in soup.find_all('div', class_="yt-lockup-content"):
        chan_name = chan_sub.find('a')['title']
        chan_id = chan_sub.find('a')['href'].split("/")[-1]
        sub_d = chan_sub.find(class_='yt-subscription-button-subscriber-count-unbranded-horizontal yt-uix-tooltip')
        sub_raw = sub_d["title"] if sub_d is not None and sub_d.get("title") else "0"
        sub_c = expand_num(sub_raw)
        sub_l.append((chan_id, chan_name, str(sub_c)))
    """
    try:
        page_info_str = [l for l in html.split("\n") if 'window["ytInitialData"] = ' in l][0]
        page_info_str = page_info_str.replace('window["ytInitialData"] = ', '').strip().rstrip(';')
        page_info_d = json.loads(page_info_str)
        sub_chan_l = []
        for tab_d in page_info_d['contents']['twoColumnBrowseResultsRenderer']['tabs']:
            try:
                sub_chan_l = tab_d['tabRenderer']['content']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents'][0]['gridRenderer']['items']
                break
            except:
                continue
    except:
        return []
    sub_l = []
    for sub_chan_d in sub_chan_l:
        try:
            chan_id = sub_chan_d['gridChannelRenderer']['channelId']
            chan_name = sub_chan_d['gridChannelRenderer']['title']["simpleText"]
        except:
            continue
        try:
            vid_c_raw = sub_chan_d['gridChannelRenderer']["videoCountText"]["runs"][0]["text"]
            videos_c = int(vid_c_raw.replace(" videos", "").replace(",", ""))
        except:
            videos_c = -1
        try:
            subs_c_raw = sub_chan_d['gridChannelRenderer']["subscriberCountText"]["runs"][0]["text"]
            subs_c = int(expand_num(subs_c_raw.replace(" subscribers", "")))
        except:
            subs_c = -1
        sub_l.append((chan_id, chan_name, str(subs_c), str(videos_c)))
    return sub_l


def scrape_all_channels(in_fp, out_fp, aws_access_key_id, aws_secret_access_key):
    # Append if file exists!
    if os.path.exists(out_fp):
        already_scraped = set([l.split("\t")[0] for l in open(out_fp)])
        of = open(out_fp, "a")
        print("ALREADY SCRAPED:", len(already_scraped))
    else:
        already_scraped = set([])
        of = open(out_fp, "w")
        print("FRESH FILE.")
    # Scrape all unscraped channels
    chan_id_l = [l.strip() for l in open(in_fp) if l.strip() not in already_scraped]
    random.shuffle(chan_id_l)
    print("SCRAPING:", len(chan_id_l))
    time_l = []
    mv_error_c = 0
    no_subs_c = 0
    for channel_id in chan_id_l:
        url = "https://www.youtube.com/channel/%(channel_id)s/channels" % vars()
        print(url)
        """
        try:
            page = requests.get(url)
        except:
            print(datetime.datetime.now(), "EXCEPTION THROWN")
            time.sleep(2)
            continue
        """
        html = subprocess.Popen('curl "%(url)s"' % vars(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf8', shell=True).communicate()[0]
        if "<TITLE>302 Moved</TITLE></HEAD><BODY>" in html:
            mv_error_c += 1
        else:
            mv_error_c = 0
        time.sleep(2)
        sub_l = scrape_subscriptions(html)
        if len(sub_l) == 0:
            print("NO SUBSCRIPTIONS.")
            of.write("\t".join([channel_id] + ["", "", ""]) + "\n")
            no_subs_c += 1
        else:
            for sub_tpl in sub_l:
                of.write("\t".join([channel_id] + list(sub_tpl)) + "\n")
            print("NUM SUBS:", len(sub_l))
            no_subs_c = 0
        time_l.append(datetime.datetime.now())
        if len(time_l) > 5:
            avg_scrape_time_str = "%.2f" % ((time_l[-1] - time_l[-6]).seconds / 5.0)
            print("LAST 5 AVG SCRAPE TIME:", avg_scrape_time_str)
        if mv_error_c >= 5 or no_subs_c >= 100:
            print("JOB FAILED.")
            os.system("touch %(out_fp)s.FAILED" % vars())
            scrape_email_util.send_email(aws_access_key_id, aws_secret_access_key, "SUB SCRAPE FINISHED - FAILED - " + in_fp, out_fp)
            of.close()
            sys.exit(1)
    of.close()
    #scrape_email_util.send_email(aws_access_key_id, aws_secret_access_key, "SUB SCRAPE FINISHED - SUCCESS - " + in_fp, in_fp)
    os.system("touch %(out_fp)s.SUCCESS" % vars())
    
if __name__ == '__main__':
    scrape_all_channels(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
