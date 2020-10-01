import sys

of = open(sys.argv[3], "w")

covered_chan_s = set([])
for line in open(sys.argv[1]):
    chan_id, lab = line.strip("\n").split("\t")
    of.write(line)
    covered_chan_s.add(chan_id)
for line in open(sys.argv[2]):
    chan_id, lab = line.strip("\n").split("\t")
    if chan_id not in covered_chan_s:
        of.write(line)
of.close()
