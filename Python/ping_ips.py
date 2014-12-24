#!/usr/bin/python
# author: wangkai
# date: 2014-08-19

import os
import sys
import subprocess
import optparse

current_dir = os.path.split(os.path.realpath(__file__))[0]
ip_list_file = os.path.join(current_dir, '/opt/zabbix_ping.list')
ip_list_progress = os.path.join(current_dir, '/tmp/zabbix_ping.progress')

def ping_ip(count, ip_address):
    sub = subprocess.Popen('ping -i 0.1 -c %s %s' % (count, ip_address), shell=True,
          stdout = subprocess.PIPE,
          stderr = subprocess.STDOUT)
    ping_result = sub.stdout.readlines()
    regular_result = []
    for line in ping_result:
        line = line.strip('\n')
        if 'time=' in line:
            regular_result.append(line)

    loss_rate = round((1 - (len(regular_result) / 1.0 / count)) * 100, 4)

    delay_result = []
    for line in regular_result:
        line_delay = line.split('=')[-1].split()[0]
        delay_result.append(float(line_delay))

    delay_count = len(delay_result) 
    del_count = int(delay_count * 0.2)
    delay_start_index = del_count
    delay_end_index = 1 - del_count
    delay_result.sort()
    delay = sum(delay_result[delay_start_index:delay_end_index]) / 1.0 / len(delay_result[delay_start_index:delay_end_index])
  
    if loss_rate == 100:
        connect = False
    else:
        connect = True

    return {"loss": loss_rate, "delay": delay, "connect": connect, "delay_result": delay_result}

def main():
    parser = optparse.OptionParser()
    parser.add_option("-c", "--count", dest = "count", metavar = "Count")
    parser.add_option("-l", "--loss", dest = "loss", metavar = "Loss")
    parser.add_option("-d", "--delay", dest = "delay", metavar = "Delay")

    (options, args) = parser.parse_args()

    count = int(options.count)

    f = open(ip_list_file)
    ip_list = f.readlines()
    f.close

    if os.path.isfile(ip_list_progress):
        f = open(ip_list_progress)
        try:
            progress = int(f.read())
        except:
            progress = 0
        f.close()
    else:
        f = open(ip_list_progress,"w")
        f.write('0')
        f.close()
        progress = 0
 
    progress = progress + 1 
    if progress >= len(ip_list):
        progress = 0

    ip = ip_list[progress].strip('\n')
    ip_name = ip.split(':')[0]
    ip_address = ip.split(':')[1]
    result = ping_ip(count, ip_address)

    if result["connect"] == False:
        print "ERROR: ping", ip_name, ip_address, "disconnect"
    elif result["loss"] >= float(options.loss):
        print "ERROR: ping", ip_name, ip_address, result["loss"], "% >", options.loss, "%"
    elif result["delay"] >= float(options.delay):
        print "ERROR: ping", ip_name, ip_address, result["delay"], "ms >", options.delay, "ms"
    else:
        print "OK: ping", ip_name, ip_address
        f = open(ip_list_progress,"w")
        f.write(str(progress))
        f.close()

if __name__ == "__main__":
    main()
