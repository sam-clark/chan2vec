import sys

tag1 = sys.argv[1]
tag2 = sys.argv[2]

tag1_chan_prob = {}
tag2_chan_prob = {}
for line in open(sys.argv[3]):
    chan_id, pol_prob, soft_tag, soft_tag_prob = line.strip("\n").split("\t")
    if soft_tag == tag1:
        tag1_chan_prob[chan_id] = float(soft_tag_prob)
    if soft_tag == tag2:
        tag2_chan_prob[chan_id] = float(soft_tag_prob)

chan_subs_d = {}
chan_name_d = {}
for line in open(sys.argv[4]):
    chan_id, chan_int, chan_name, scrap_subs, subs = line.strip("\n").split("\t")
    if chan_id in tag1_chan_prob or chan_id in tag2_chan_prob:
        chan_subs_d[chan_id] = int(subs)
        chan_name_d[chan_id] = chan_name

found_c = 0
for chan_id, subs in sorted(chan_subs_d.items(), key=lambda x: x[1], reverse=True):
    t1_pred = 0.0 if chan_id not in tag1_chan_prob else tag1_chan_prob[chan_id]
    t2_pred = 0.0 if chan_id not in tag2_chan_prob else tag2_chan_prob[chan_id]
    if t1_pred <= 0.5 and t2_pred <= 0.5:
        continue
    print(";".join([chan_id, chan_name_d[chan_id], str(subs), str(t1_pred), str(t2_pred)]))
    found_c += 1
    if found_c >= 20:
        break
