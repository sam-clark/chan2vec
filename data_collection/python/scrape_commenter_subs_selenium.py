import re
import sys
import time
import os
import random
import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from pyvirtualdisplay import Display

import scrape_email_util

display = Display(visible=0, size=(1920, 1080))
display.start()
driver = webdriver.Chrome()


def parse_subs(html):
    sub_l = []
    for chan_seg in html.split('<div id="channel" class="style-scope ytd-grid-channel-renderer">')[1:]:
        m = re.search('href="/channel/([^\"]+)">', chan_seg)
        if m is None: continue
        chan_id = m.group(1)
        m = re.search('<span id="title" class="style-scope ytd-grid-channel-renderer">([^\<]+)</span>', chan_seg)
        chan_name = m.group(1) if m is not None else ""
        m = re.search('<span id="thumbnail-attribution" class="style-scope ytd-grid-channel-renderer">(.+) subscribers</span>', chan_seg)
        sub_raw = m.group(1) if m is not None else "-1"
        if sub_raw[-1] == "M":
            sub_c = float(sub_raw[:-1])*1000000
        elif sub_raw[-1] == "K":
            sub_c = float(sub_raw[:-1])*1000
        else:
            sub_c = float(sub_raw)
        sub_l.append((chan_id, chan_name, str(sub_c)))
    return sub_l

aws_access_key_id = sys.argv[3]
aws_secret_access_key = sys.argv[4]

# Make file if doesn't exist, otherwise collect previously scraped channels
out_fp = sys.argv[2]
already_scraped_s = set([])
if not os.path.exists(out_fp):
    of = open(out_fp, "w")
else:
    for line in open(out_fp):
        already_scraped_s.add(line.split("\t")[0])
    of = open(out_fp, "a")
        
print("Already scraped: ", len(already_scraped_s))

commenter_fp = sys.argv[1]
chan_id_l = [l.strip() for l in open(commenter_fp)]
random.shuffle(chan_id_l)

no_sub_c = 0
for lid, channel_id in enumerate(chan_id_l):
    if channel_id == "" or channel_id in already_scraped_s:
        continue
    url = "https://www.youtube.com/channel/" + channel_id + "/channels"
    print("Scraping:", url)
    driver.get(url)
    time.sleep(3)
    # Scroll until no new subs are found for 2 scrolls
    fail_inc_c = 0
    scroll_c = 0
    last_sub_c = 0
    last_inc_html = ""
    while fail_inc_c < 2:
        scroll_amount = str((scroll_c+1)*20000)
        driver.execute_script("window.scrollTo(0, %(scroll_amount)s);" % vars())
        time.sleep(2)
        html = driver.page_source.encode("ascii", "ignore").decode()
        num_subs = len(html.split('<div id="channel" class="style-scope ytd-grid-channel-renderer">'))
        if num_subs < last_sub_c:
            break
        elif num_subs == last_sub_c:
            fail_inc_c += 1
        else:
            last_inc_html = html
            fail_inc_c = 0
        scroll_c += 1
        last_sub_c = num_subs
        print(scroll_c, fail_inc_c, num_subs)
        if num_subs >= 1000:
            break
    # Keep track of number of times in a row no subs were found
    if num_subs == 0:
        no_sub_c += 1
    else:
        no_sub_c = 0
    # Output ALL subs data
    print(datetime.datetime.now())
    already_scraped_s.add(channel_id)
    sub_l = parse_subs(last_inc_html)
    if not sub_l:
        of.write("\t".join([channel_id, "", "", ""]) + "\n")
    else:
        for tpl in sub_l:
            of.write("\t".join((channel_id,) + tpl) + "\n")
    # Stop if continuing to fail
    if no_sub_c >= 15:
        scrape_email_util.send_email(aws_access_key_id, aws_secret_access_key, "SUB SEL SCRAPE FINISHED - FAILED - " + commenter_fp, commenter_fp)
        os.system("touch %(out_fp)s.FAILED" % vars())
        of.close()
        sys.exit(1)
        break

#scrape_email_util.send_email(aws_access_key_id, aws_secret_access_key, "SUB SEL SCRAPE FINISHED - SUCCESS - " + commenter_fp, commenter_fp)
of.close()
os.system("touch %(out_fp)s.SUCCESS" % vars())

driver.close()
display.stop()

