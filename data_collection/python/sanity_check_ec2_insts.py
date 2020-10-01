import sys
import os

for line in open(sys.argv[1]):
    ec2_ip = line.strip()
    cmd = 'ssh %(ec2_ip)s "ls -l /home/ubuntu/"' % vars()
    print(cmd)
    os.system(cmd)
    
