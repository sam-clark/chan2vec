import sys
import random

targ_tag = sys.argv[1]

def get_chans(targ_tag, fp):
    chan_s = set([])
    for line in open(fp):
        chan_id, _, tag, tag_prob = line.strip("\n").split("\t")
        if float(tag_prob) >= 0.5 and tag == targ_tag:
            chan_s.add(chan_id)
    return chan_s

old_s = get_chans(targ_tag, sys.argv[2])
new_s = get_chans(targ_tag, sys.argv[3])

diff_l = list(new_s.difference(old_s))
random.shuffle(diff_l)

for chan_id in diff_l:
    print(chan_id)
