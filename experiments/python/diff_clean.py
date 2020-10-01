import sys

old_s = set([l.strip("\n") for l in open(sys.argv[1])])

new_l = [l.strip("\n") for l in open(sys.argv[2])]

of = open(sys.argv[3], "w")
for l in sorted(new_l):
    if l not in old_s:
        of.write(l + "\n")
of.close()

