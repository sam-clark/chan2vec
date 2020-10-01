import random
import argparse
import os
import time
import sys
import subprocess
import datetime

COMMENT_SCRAPE = 'comment_scrape'
SUBS_CURL_SCRAPE = 'subs_curl_scrape'
SUBS_SELENIUM_SCRAPE = 'subs_selenium_scrape'
VIDEO_CURL_SCRAPE = 'video_curl_scrape'

def start_batch_scrape(scrape_ids_fp, ec2_ip_fp, work_dir, data_loc_fp,
                       ec2_setup_script_fp, scrape_type,
                       aws_access_id, aws_secret_key,
                       num_jobs_per_inst=2, skip_install=False, scrape_date=None):
    if scrape_type == COMMENT_SCRAPE:
        scrape_script_fp = './data_collection/python/scrape_comments.py'
    elif scrape_type == SUBS_CURL_SCRAPE:
        scrape_script_fp = './data_collection/python/scrape_commenter_subs_curl.py'
    elif scrape_type == SUBS_SELENIUM_SCRAPE:
        scrape_script_fp = './data_collection/python/scrape_commenter_subs_selenium.py'
    elif scrape_type == VIDEO_CURL_SCRAPE:
        scrape_script_fp = './data_collection/python/scrape_channel_latest_videos.py'
    else:
        print("SCRAPE TYPE NOT SUPPORTED:", scrape_type)
        sys.exit(1)
    if not os.path.exists(work_dir):
        os.makedirs(work_dir)
    ec2_ip_l = [l.strip() for l in open(ec2_ip_fp)]
    num_ec2_insts = len(ec2_ip_l)
    scrape_ids_l = [l.strip("\n") for l in open(scrape_ids_fp)]
    # Split up vids
    # Shuffle so that jobs take a similar amount of time
    num_files = num_ec2_insts*num_jobs_per_inst
    num_lines_per_file = int(len(scrape_ids_l)/num_files) + 1
    random.shuffle(scrape_ids_l)
    scrape_data_fp_l = []
    for i in range(num_files):
        if scrape_type == COMMENT_SCRAPE:
            fp = work_dir + "/vid_ids.txt." + str(i)
            of = open(fp, "w")
            of.write("\n".join(["\t".join(line.split("\t")[0:2]) for line
                                in scrape_ids_l[i*num_lines_per_file:(i+1)*num_lines_per_file]]))
            of.close()
            scrape_data_fp_l.append(fp)
        else:
            if scrape_type == SUBS_CURL_SCRAPE:
                fp = work_dir + "/commenter_ids.txt." + str(i)
            elif scrape_type == VIDEO_CURL_SCRAPE:
                fp = work_dir + "/chan_ids.txt." + str(i)
            else:
                fp = work_dir + "/commenter_need_sel_ids.txt." + str(i)
            of = open(fp, "w")
            of.write("\n".join([line for line in scrape_ids_l[i*num_lines_per_file:(i+1)*num_lines_per_file]]))
            of.close()
            scrape_data_fp_l.append(fp)
    # Install packages on each machine (in parallel)
    if not skip_install:
        # Copy over and run script to install necessary packages
        install_in_prog_l = []
        for ec2_ip in ec2_ip_l:
            cmd = "scp %(ec2_setup_script_fp)s %(ec2_ip)s:/home/ubuntu/" % vars()
            os.system(cmd)
            ec2_setup_script_fn = ec2_setup_script_fp.split("/")[-1]
            cmd = 'ssh %(ec2_ip)s "nohup /home/ubuntu/%(ec2_setup_script_fn)s  > /home/ubuntu/INSTALL.stdout 2> /home/ubuntu/INSTALL.stderr &"' % vars()
            print(cmd)
            os.system(cmd)
            install_in_prog_l.append(ec2_ip)
        # Wait for scripts to finish installing
        success_fp_loc = "/home/ubuntu/_SUCCESS"
        while len(install_in_prog_l) > 0:
            print("WAITING FOR INSTALLS - ", datetime.datetime.now(), len(install_in_prog_l))
            install_in_prog_l_temp = []
            for ec2_ip in install_in_prog_l:
                ls_res = subprocess.Popen('ssh %(ec2_ip)s "ls -l %(success_fp_loc)s"' % vars(),
                                          shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
                if success_fp_loc not in str(ls_res):
                    install_in_prog_l_temp.append(ec2_ip)
            install_in_prog_l = install_in_prog_l_temp
            time.sleep(1)
    # Start jobs on each machine
    fp_c = 0
    of_ec2_data = open(data_loc_fp, "w")
    for ec2_ip in ec2_ip_l:
        # Copy over script to run for scraping
        scrape_script_fn = scrape_script_fp.split("/")[-1]
        cmd = "scp %(scrape_script_fp)s %(ec2_ip)s:/home/ubuntu/python/" % vars()
        os.system(cmd)
        os.system("scp data_collection/python/scrape_email_util.py %(ec2_ip)s:/home/ubuntu/python/" % vars())
        # Copy over data and start scraping
        for job_num in range(1,num_jobs_per_inst+1):
            data_fp = scrape_data_fp_l[fp_c]
            data_fn = data_fp.split("/")[-1]
            ec2_data_fp = "/home/ubuntu/data/" + data_fn
            cmd = "scp %(data_fp)s %(ec2_ip)s:%(ec2_data_fp)s" % vars()
            os.system(cmd)
            print(cmd)
            # Select command
            if scrape_type == COMMENT_SCRAPE:
                ec2_data_out1_fp = ec2_data_fp + ".cat_info"
                ec2_data_out2_fp = ec2_data_fp + ".comments"
                scrape_cmd = "python3 /home/ubuntu/python/%(scrape_script_fn)s %(ec2_data_fp)s %(ec2_data_out1_fp)s %(ec2_data_out2_fp)s %(aws_access_id)s %(aws_secret_key)s" % vars()
                cmd = 'ssh %(ec2_ip)s "nohup env PATH=$PATH:/home/ubuntu/ %(scrape_cmd)s > %(ec2_data_out1_fp)s.stdout 2> %(ec2_data_out1_fp)s.stderr &"' % vars()
                of_ec2_data.write(ec2_ip + ":" + ec2_data_out1_fp + "\n")
                of_ec2_data.write(ec2_ip + ":" + ec2_data_out2_fp + "\n")
            elif scrape_type == SUBS_CURL_SCRAPE:
                ec2_data_out_fp = ec2_data_fp + ".subs"
                scrape_cmd = "python3 /home/ubuntu/python/%(scrape_script_fn)s %(ec2_data_fp)s %(ec2_data_out_fp)s %(aws_access_id)s %(aws_secret_key)s" % vars()
                cmd = 'ssh %(ec2_ip)s "nohup %(scrape_cmd)s > %(ec2_data_out_fp)s.stdout 2> %(ec2_data_out_fp)s.stderr &"' % vars()
                of_ec2_data.write(ec2_ip + ":" + ec2_data_out_fp + "\n")
            elif scrape_type == SUBS_SELENIUM_SCRAPE:
                ec2_data_out_fp = ec2_data_fp + ".sel_subs"
                scrape_cmd = "python3 /home/ubuntu/python/%(scrape_script_fn)s %(ec2_data_fp)s %(ec2_data_out_fp)s %(aws_access_id)s %(aws_secret_key)s" % vars()
                cmd = 'ssh %(ec2_ip)s "nohup env PATH=$PATH:/home/ubuntu/ %(scrape_cmd)s > %(ec2_data_out_fp)s.stdout 2> %(ec2_data_out_fp)s.stderr &"' % vars()
                of_ec2_data.write(ec2_ip + ":" + ec2_data_out_fp + "\n")
            elif scrape_type == VIDEO_CURL_SCRAPE:
                ec2_data_out_fp = ec2_data_fp + ".vids"
                scrape_cmd = "python3 /home/ubuntu/python/%(scrape_script_fn)s --chan-fp %(ec2_data_fp)s --out-fp %(ec2_data_out_fp)s --scrape-date %(scrape_date)s" % vars()
                cmd = 'ssh %(ec2_ip)s "nohup %(scrape_cmd)s > %(ec2_data_out_fp)s.stdout 2> %(ec2_data_out_fp)s.stderr &"' % vars()
                of_ec2_data.write(ec2_ip + ":" + ec2_data_out_fp + "\n")
            # Run command
            print(cmd)
            os.system(cmd)
            time.sleep(2)

            fp_c += 1
    of_ec2_data.close()

    
if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--scrape-ids-fp')
    parser.add_argument('--ec2-ip-fp')
    parser.add_argument('--work-dir')
    parser.add_argument('--data-loc-fp')
    parser.add_argument('--aws-access-id')
    parser.add_argument('--aws-secret-key')
    parser.add_argument('--ec2-setup-script-fp',
                        default='./data_collection/sh/ec2_selenium_setup.sh')
    parser.add_argument('--scrape-type')
    parser.add_argument('--num-jobs-per-inst', type=int, default=2)
    parser.add_argument('--skip-install', type=bool, default=False)
    parser.add_argument('--scrape-date', default=None)
    args=parser.parse_args()
    start_batch_scrape(args.scrape_ids_fp, args.ec2_ip_fp, args.work_dir, args.data_loc_fp,
                       args.ec2_setup_script_fp, args.scrape_type,
                       args.aws_access_id, args.aws_secret_key,
                       num_jobs_per_inst=args.num_jobs_per_inst,
                       skip_install=args.skip_install,
                       scrape_date=args.scrape_date)
