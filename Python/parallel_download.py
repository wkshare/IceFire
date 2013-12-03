#!/usr/bin/python

import urllib
import urllib2
import urlparse
import os
import sys
import logging
import multiprocessing
import signal
import re
import socket

socket.setdefaulttimeout(6.0)

process_sum = 24

get_dir = 'ImgFullPath'
save_dir = '/disk3/leishi_data'
list_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),get_dir)

continue_point = {
    'ImgFullPath_20131121171608.txt':0
}

logging.basicConfig(filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'run.log'), level=logging.DEBUG, format = '%(asctime)s - %(levelname)s: %(message)s')

def handler(signum, frame):
    sys.exit(1)

def get_file(url, filename, i):
    signal.signal(signal.SIGTERM, handler)
    signal.signal(signal.SIGINT, handler)

    m = re.search('http.*$', url)
    if m:
        url = m.group(0)
    else:
        logging.debug('%s format failed %s %s' % (url, filename, i))
    url_split = url.split('//')
    file_local_path = os.path.join(save_dir, url_split[1])
    file_local_dir = os.path.dirname(file_local_path)
    if not os.path.isdir(file_local_dir):
        os.makedirs(file_local_dir)
    try:
        urllib.urlretrieve(url, file_local_path)
        logging.debug('%s download success %s %s ' % (url, filename, i))
    except Exception, e:
        #logging.debug('%s download retry %s %s ' % (url, filename, i))
        logging.debug('%s download failed %s %s' % (url, filename, i))

def main():
    pool = multiprocessing.Pool(processes = process_sum)
    for l in os.listdir(list_dir):
        filename = os.path.join(list_dir,l)
        f = open(filename)
        lines = f.readlines()
        f.close()
        
        if (l in continue_point) and (continue_point[l] == -1):
            continue
        
        i = 1
        for url in lines:
            if (l in continue_point) and (i < continue_point[l]):
                i += 1
                continue
            url = url.strip()
            #get_file(url, l, str(i))
            pool.apply_async(get_file, (url, l, str(i), ))
            i += 1
    pool.close()
    pool.join()
    
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logging.debug(' process exit.')
        sys.exit(1)
