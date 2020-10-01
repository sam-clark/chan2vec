import sys

vid_id_s = set([l.split("\t")[1] for l in open(sys.argv[1])])

of = open(sys.argv[4], "w")
for fp in [sys.argv[2], sys.argv[3]]:
    for l in open(fp):
        tpl = l.split("\t")
        if len(tpl) < 2: continue
        vid_id = tpl[1]
        if vid_id in vid_id_s:
            of.write(l)
of.close()
