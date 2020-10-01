import sys
import os
import time
import random
import datetime
import json

import argparse

import subprocess


def age_conv(age_raw):
    age_tpl = age_raw.replace("Streamed ", "").split(" ")
    try:
        num = float(age_tpl[0])
    except:
        return -1
    if "hour" in age_tpl[1] or "minute" in age_tpl[1]:
        return 0
    if "day" in age_tpl[1]:
        return num
    elif "week" in age_tpl[1]:
        return num*7
    elif "month" in age_tpl[1]:
        return num*30
    elif "year" in age_tpl[1]:
        return num*365
    else:
        return -1


def parse_videos(html):
    try:
        page_info_str = [l for l in html.split("\n") if 'window["ytInitialData"] = ' in l][0]
        page_info_str = page_info_str.replace('window["ytInitialData"] = ', '').strip().rstrip(';')
        page_info_d = json.loads(page_info_str)
        vid_l = []
        for tab_d in page_info_d['contents']['twoColumnBrowseResultsRenderer']['tabs']:
            try:
                vid_l = tab_d['tabRenderer']['content']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents'][0]['gridRenderer']['items']
                break
            except:
                continue
    except:
        print('VID PARSE ERROR.')
        return []
    vid_out_l = []
    for vid_d in vid_l:
        try:
            vid_id = vid_d['gridVideoRenderer']['videoId']
            if 'simpleText' in vid_d['gridVideoRenderer']['title']:
                title = vid_d['gridVideoRenderer']['title']["simpleText"]
            else:
                title = vid_d['gridVideoRenderer']['title']['runs'][0]['text']
        except:
            continue
        try:
            views_raw = vid_d['gridVideoRenderer']["viewCountText"]["simpleText"]
            views = views_raw.replace(" views", "").replace(",", "")
        except:
            views = ""
        try:
            vid_age_raw = vid_d['gridVideoRenderer']["publishedTimeText"]["simpleText"]
        except:
            vid_age_raw = ""
        vid_out_l.append((vid_id, views, vid_age_raw, title))
    return vid_out_l


def scrape_channel_vids(in_fp, out_fp, scrape_date_str, num_retries=5):
    # Append if file exists
    if os.path.exists(out_fp):
        already_scraped = set([l.split("\t")[0] for l in open(out_fp)])
        of = open(out_fp, "a")
        print("ALREADY SCRAPED:", len(already_scraped))
    else:
        already_scraped = set([])
        of = open(out_fp, "w")
        print("FRESH FILE.")
    # Scrape all unscraped channels
    scrape_date_o = datetime.datetime.strptime(scrape_date_str, "%Y-%m-%d")
    chan_id_l = [l.strip().split("/")[-1] for l in open(in_fp)]
    random.shuffle(chan_id_l)
    time_l = []
    for channel_id in chan_id_l:
        if channel_id in already_scraped:
            continue
        for try_num in range(1,num_retries+1):
            # Try two different ways of formating the URL
            if try_num % 2 == 0:
                url = "https://www.youtube.com/channel/%(channel_id)s/videos" % vars()
            else:
                url = "https://www.youtube.com/channel/%(channel_id)s/videos?view=0&sort=dd&shelf_id=0" % vars()
            print("Scraping:", url)
            """
            try:
                page = requests.get(url)
            except:
                print("PAGE LOAD EXCEPTION - RETRY: ", try_num)
                continue
            time.sleep(1)
            """
            html = subprocess.Popen('curl "%(url)s"' % vars(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf8', shell=True).communicate()[0]
            vid_l = parse_videos(html)
            time.sleep(2)
            if len(vid_l) > 0:
                break
            else:
                print("NO VIDS - RETRY: ", try_num)
                time.sleep(2)
        if len(vid_l) == 0:
            print("NO VIDEOS - FINAL.")
            of.write("\t".join([channel_id, "", "", "", "", ""]) + "\n")
        else:
            for vid_id, views, vid_age_raw, title in vid_l:
                days_old = age_conv(vid_age_raw)
                if days_old == -1:
                    date_posted = ""
                else:
                    date_posted = (scrape_date_o - datetime.timedelta(days=days_old)).strftime("%Y-%m-%d")
                of.write("\t".join([channel_id, vid_id, views, vid_age_raw, date_posted, title]) + "\n")
            print("NUM VIDS:", len(vid_l))
        time_l.append(datetime.datetime.now())
        if len(time_l) > 5:
            avg_scrape_time_str = "%.2f" % ((time_l[-1] - time_l[-6]).seconds / 5.0)
            print("LAST 5 AVG SCRAPE TIME: " + str(avg_scrape_time_str), file=sys.stderr)
    of.close()
    os.system("touch %(out_fp)s.SUCCESS" % vars())

    
if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--chan-fp')
    parser.add_argument('--out-fp')
    parser.add_argument('--scrape-date')
    parser.add_argument('--num-retries', type=int, default=5)
    args=parser.parse_args()
    scrape_channel_vids(args.chan_fp, args.out_fp, args.scrape_date, num_retries=args.num_retries)
