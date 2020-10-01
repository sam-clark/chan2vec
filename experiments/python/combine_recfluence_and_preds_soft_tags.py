import sys

filt_fp = sys.argv[1]
rec_fp = sys.argv[2]
preds_fp = sys.argv[3]
out_fp = sys.argv[4]

filt_s = set([l.strip() for l in open(filt_fp)])

of = open(out_fp, "w")
for line in open(rec_fp):
    chan_id, soft_tag = line.strip("\n").split("\t")
    if chan_id not in filt_s:
        of.write("\t".join([chan_id, "1.0", soft_tag, "1.0"]) + "\n")
for line in open(preds_fp):
    of.write(line)
of.close()
