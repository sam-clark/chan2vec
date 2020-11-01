import sys
import random

keep_tags_s = set(sys.argv[1].split(","))

# Get chans with old tags that need to be kept
kept_chan_s = set([])
for line in open(sys.argv[2]):
    chan_id, _, tag, tag_prob = line.strip("\n").split("\t")
    if float(tag_prob) >= 0.5 and tag in keep_tags_s:
        kept_chan_s.add(chan_id)

# Keep all tags for these
of = open(sys.argv[4], "w")
for line in open(sys.argv[2]):
    chan_id, _, tag, tag_prob = line.strip("\n").split("\t")
    if chan_id in kept_chan_s:
        of.write(line)

# Use all new tags unless channel
for line in open(sys.argv[3]):
    chan_id, _, tag, tag_prob = line.strip("\n").split("\t")
    if chan_id in kept_chan_s:
        continue
    if float(tag_prob) >= 0.5 and tag in keep_tags_s:
        continue
    of.write(line)

of.close()
