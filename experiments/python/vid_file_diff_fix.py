import sys

chan_id_s = set([l.strip("\n").split("\t")[0] for l in open(sys.argv[1])])

of = open(sys.argv[4], "w")
for fp in [sys.argv[2], sys.argv[3]]:
    for l in open(fp):
        chan_id = l.strip("\n").split("\t")[0]
        if chan_id in chan_id_s:
            of.write(l)
of.close()
