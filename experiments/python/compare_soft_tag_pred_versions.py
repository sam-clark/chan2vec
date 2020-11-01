import sys
import collections

old_fp = sys.argv[1]
new_fp = sys.argv[2]

def get_tags(fp):
    chan_tag_s = {}
    for line in open(fp):
        chan_id, _, tag, tag_prob = line.strip("\n").split("\t")
        if float(tag_prob) >= 0.5:
            if chan_id not in chan_tag_s:
                chan_tag_s[chan_id] = set([])
            chan_tag_s[chan_id].add(tag)
    return chan_tag_s

old_chan_tag_s = get_tags(old_fp)
new_chan_tag_s = get_tags(new_fp)

diff_tags_c = 0
for chan_id, old_tag_s in old_chan_tag_s.items():
    if chan_id in new_chan_tag_s and len(new_chan_tag_s[chan_id].union(old_tag_s)) > len(old_tag_s):
        diff_tags_c += 1
        

print("Overall channel differences:")
print("Old chans:", len(old_chan_tag_s))
print("New chans:", len(new_chan_tag_s))
print("Old uniq:", len(set(old_chan_tag_s.keys()).difference(set(new_chan_tag_s.keys()))))
print("New uniq:", len(set(new_chan_tag_s.keys()).difference(set(old_chan_tag_s.keys()))))
print("Same chans:", len(set(new_chan_tag_s.keys()).intersection(set(old_chan_tag_s.keys()))))
print("Same chans + diff tags:", diff_tags_c)
print()

def get_tag_c(chan_tag_s):
    tag_chan_d = {}
    for chan_id, tag_s in chan_tag_s.items():
        for tag in tag_s:
            if tag not in tag_chan_d:
                tag_chan_d[tag] = set([])
            tag_chan_d[tag].add(chan_id)
    return tag_chan_d

old_tag_chan_d = get_tag_c(old_chan_tag_s)
new_tag_chan_d = get_tag_c(new_chan_tag_s)

print("Tag Counts:")
for tag, old_chan_s in sorted(old_tag_chan_d.items(), key=lambda x: len(x[1]), reverse=True):
    
    print("\t".join([str(len(old_chan_s)), str(len(new_tag_chan_d[tag])), tag]))
print()


def get_tag_pairs_c(chan_tag_s):
    pair_chans_d = collections.defaultdict(set)
    for chan_id, tag_s in chan_tag_s.items():
        for tag1 in tag_s:
            for tag2 in tag_s:
                if tag1 not in set(["L", "C", "R"]) and tag2 not in set(["L", "C", "R"]) and tag1 != tag2:
                    pair_chans_d[(tag1, tag2)].add(chan_id)
    return pair_chans_d

old_pair_chans_d = get_tag_pairs_c(old_chan_tag_s)
new_pair_chans_d = get_tag_pairs_c(new_chan_tag_s)

print("Tag pairs diff:")
used_pairs = set([])
for pair, old_chan_s in sorted(old_pair_chans_d.items(), key=lambda x: len(x[1]), reverse=True):
    if len(old_chan_s) <= 20:
        break
    if pair in used_pairs:
        continue
    print("\t".join([str(len(old_chan_s)), str(len(new_pair_chans_d[pair])), str(pair)]))
    used_pairs.add((pair[1], pair[0]))
