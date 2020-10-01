import argparse
import subprocess
import datetime
import time
import os
import sys


def check_file_exists(ec2_ip, flag_fp):
    ls_res = subprocess.Popen('ssh %(ec2_ip)s "ls -l %(flag_fp)s"' % vars(),
                              shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
    return flag_fp in str(ls_res)


def check_file_flags(data_loc_fp, sub_string, email, seconds_sleep=300):
    file_info_l = [ec2_file_fp.strip("\n").split(":") for ec2_file_fp in open(data_loc_fp)
                   if sub_string in ec2_file_fp]
    success_c = 0
    failed_c = 0
    while len(file_info_l) > 0:
        # Check all files
        print(datetime.datetime.now())
        file_info_l_temp = []
        for ec2_ip, file_fp in file_info_l:
            success_fp = file_fp + ".SUCCESS"
            failed_fp = file_fp + ".FAILED"
            if check_file_exists(ec2_ip, success_fp):
                success_c += 1
                print("SUCCESS\t" + file_fp + "\t" + ec2_ip)
            elif check_file_exists(ec2_ip, failed_fp):
                failed_c += 1
                print("FAILED\t" + file_fp + "\t" + ec2_ip)
            else:
                file_info_l_temp.append((ec2_ip, file_fp))
                print("NO RES\t" + file_fp + "\t" + ec2_ip)
        print()
        print("SUCCESS:", success_c)
        print("FAILED:", failed_c)
        print("NO RES:", len(file_info_l_temp))
        print()
        file_info_l = file_info_l_temp
        if file_info_l:
            time.sleep(seconds_sleep)
    # Notify when finished
    body = "SUCCESS: %(success_c)d \n FAILED: %(failed_c)d" % vars()
    cmd = 'echo "%(body)s" | mail -s "SCRAPING FINISHED." %(email)s' % vars()
    os.system(cmd)



if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--data-loc-fp')
    parser.add_argument('--sub-string', default='')
    parser.add_argument('--email', default='')
    parser.add_argument('--seconds-sleep', type=int, default=300)
    args=parser.parse_args()
    check_file_flags(args.data_loc_fp, args.sub_string, args.email, seconds_sleep=args.seconds_sleep)
