import sys
import time
import os
import random
import datetime
import re

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from pyvirtualdisplay import Display

import scrape_email_util


def parse_cat_info_coms_page(html):
    m = re.search(',\"category\":\"([^\"]+)\",', html)
    return None if m is None else m.group(1)


def parse_comments(html):
    # Parsing comments                                                                                                                                                                                                                      
    comment_l = []
    for comment_section in html.split('<a id="author-text" class="yt-simple-endpoint style-scope ytd-comment-renderer"')[1:]:
        # Author                                                                                                                                                                                                                            
        m = re.search('href="/channel/([^\"]*)"', comment_section)
        if m is None: continue
        author_channel = m.group(1)
        # Comment                                                                                                                                                                                                                           
        if '<span dir="auto" class="style-scope yt-formatted-string">' in comment_section:
            comment = " ".join([m.group(1).strip().replace("\t", " ") for m in re.finditer('<span dir="auto" class="style-scope yt-formatted-string">([^\<]*)<', comment_section)])
        else:
            m = re.search('id="content-text" slot="content" split-lines="" class="style-scope ytd-comment-renderer">([^\<]*)<', comment_section)
            comment = m.group(1).strip().replace("\t", " ") if m is not None else ""
        comment = comment.replace("\n", " ")
        # Likes                                                                                                                                                                                                                             
        m = re.search('<span id="vote-count-left" class="style-scope ytd-comment-action-buttons-renderer" hidden="" aria-label="([^\"]*)">', comment_section)
        likes_c = 0
        if m is not None:
            likes_raw_str = m.group(1).split(" ")[0]
            try:
                if likes_raw_str[-1] == "K":
                    likes_c = int(float(likes_raw_str[:-1])*1000)
                elif likes_raw_str[-1] == "M":
                    likes_c = int(float(likes_raw_str[:-1])*1000000)
                else:
                    likes_c = int(likes_raw_str)
            except:
                print("ERROR - Parsing Likes:", m.group(1))
        comment_l.append((author_channel, comment, str(likes_c)))
    return comment_l


display = Display(visible=0, size=(1920, 1080))
display.start()
driver = webdriver.Chrome()

cat_info_fp = sys.argv[2]
comments_fp = sys.argv[3]
if os.path.exists(cat_info_fp):
    already_scraped_s = set([l.split("\t")[0] for l in open(cat_info_fp)])
    cat_info_f = open(cat_info_fp, "a")
    comments_f = open(comments_fp, "a")
else:
    already_scraped_s = set([])
    cat_info_f = open(cat_info_fp, "w")
    comments_f = open(comments_fp, "w")

aws_access_key_id = sys.argv[4]
aws_secret_access_key = sys.argv[5]

print("Already scraped: ", len(already_scraped_s))

vid_fp = sys.argv[1]
vid_id_l = [l.strip("\n").split("\t") for l in open(vid_fp)]
random.shuffle(vid_id_l)

def get_comment_count(html):
    if "style-scope ytd-comment-renderer" in html:
        no_comments_c = 0
        # Estimate number of comments
        num_coms = len(html.split("</yt-formatted-string><yt-formatted-string id")) - 1
        return num_coms
    else:
        return 0

no_comments_c = 0
success = True
for lid, (channel_id, video_id) in enumerate(vid_id_l):
    if video_id == "" or video_id in already_scraped_s:
        continue
    url = "https://www.youtube.com/watch?v=" + video_id
    print("Scraping:", url)
    driver.get(url)
    time.sleep(3)
    com_c = 0
    last_com_c = 0
    no_improvement = 0
    for i in range(10):
        scroll_amount = str((i+1)*20000)
        driver.execute_script("window.scrollTo(0, %(scroll_amount)s);" % vars())
        time.sleep(2)
        html = driver.page_source.encode("ascii", "ignore").decode()
        com_c = get_comment_count(html)
        print(no_improvement, com_c)
        if com_c == last_com_c:
            no_improvement += 1
        else:
            no_improvement = 0
        if no_improvement >= 2:
            break
        last_com_c = com_c
    # Keep track of number of videos with no comments in a row
    if com_c > 0:
        no_comments_c = 0
    else:
        no_comments_c += 1
        print("NO COMMENTS: ", no_comments_c)
    """
    # Output ALL data for now
    ofp = out_dir + "/" + video_id + ".html"
    of = open(ofp, "w")
    of.write(html)
    of.close()
    os.system("gzip " + ofp)
    """
    # Parse and output results
    cat = parse_cat_info_coms_page(html)
    cat = cat if cat is not None else ""
    cat_info_f.write(channel_id + "\t" + video_id + "\t" + cat + "\n")
    for author_channel, comment, likes in parse_comments(html):
        comments_f.write("\t".join([channel_id, video_id, author_channel, comment, likes]) + "\n")
    print(datetime.datetime.now())
    already_scraped_s.add(video_id)
    if no_comments_c >= 20:
        os.system("touch %(comments_fp)s.FAILED" % vars())
        scrape_email_util.send_email(aws_access_key_id, aws_secret_access_key, "COMMENT SCRAPE FINISHED - FAILED - " + vid_fp, vid_fp)
        success = False
        break

driver.close()
display.stop()

cat_info_f.close()
comments_f.close()
if success:
    os.system("touch %(comments_fp)s.SUCCESS" % vars())
    #scrape_email_util.send_email(aws_access_key_id, aws_secret_access_key, "COMMENT SCRAPE FINISHED - SUCCESS - " + vid_fp, vid_fp)

