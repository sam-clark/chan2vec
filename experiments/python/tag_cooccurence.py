import sys
import collections

soft_tag_fp = sys.argv[1]
tags_str = sys.argv[2]
keep_tags_l = tags_str.split(",")
keep_tags_s = set(keep_tags_l)

chan_soft_tag_d = collections.defaultdict(set)
for line in open(soft_tag_fp):
    chan_id, pol_pred, soft_tag, st_pred_prob = line.strip("\n").split("\t")
    if float(st_pred_prob) < 0.5 or soft_tag not in keep_tags_s:
        continue
    chan_soft_tag_d[chan_id].add(soft_tag)

st_tot_c = collections.defaultdict(int)
st_st_c = collections.defaultdict(
    lambda : collections.defaultdict(int))
for soft_tag_s in chan_soft_tag_d.values():
    for st1 in soft_tag_s:
        st_tot_c[st1] += 1
        for st2 in soft_tag_s:
            st_st_c[st1][st2] += 1

# Percentages
print(";".join([""] + keep_tags_l))
for st1 in keep_tags_l:
    cols = [st1]
    for st2 in keep_tags_l:
        cols.append("%.3f" % (st_st_c[st1][st2] / st_tot_c[st1]))
    print(";".join(cols))
print()

# Raw counts
print(";".join([""] + keep_tags_l))
for st1 in keep_tags_l:
    cols = [st1]
    for st2 in keep_tags_l:
        cols.append(str(st_st_c[st1][st2]))
    print(";".join(cols))

