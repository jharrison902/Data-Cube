# -*- coding: utf-8 -*-
"""
Created on Thu Sep  3 10:55:43 2015

@author: datacube
"""

"""
Faster ingester
"""

import psutil

import argparse
from multiprocessing import Process
import re
import os

def ingest_file(can_del=False,file_paths=[],tmp_dir='/tmp/',instrument='ls7'):
    
    for file_path in file_paths:
        """
        Ingester a tar ball
        """
        #make the tmp directory
        group = re.findall('([A-Z0-9]+?)-',os.path.basename(file_path))
        if len(group) < 1:
            print "Problem with file: "+file_path
            continue
        sid = group[0] or None 
        if sid is None:
            continue
        dname = os.path.join(tmp_dir,sid)
        os.makedirs(dname)
        #untar the data
        os.system('cat '+file_path+' | pv -L 30m | tar -C '+dname+' -zx')
        #ingest the directory
        
        os.system('bash '+os.getcwd()+'/ingest_dir.sh '+dname+" "+instrument)
        if can_del:
            os.system('rm -rf '+dname)
    

if __name__ == '__main__':
    threads = []
    thread_library = []
    parser = argparse.ArgumentParser(description="Bulk Ingester for AMA implementation of agdc v1")
    parser.add_argument("-i","--instrument",required=True,type=str,help="The instrument: ls7, ls8, ls5")
    parser.add_argument("-d","--dir",required=True,type=str,help="Directory containing level 2 sr products")
    parser.add_argument("-t","--tmp",required=True,type=str,help="Directory to work in")
    parser.add_argument("-y","--yes",required=False,action="store_true",help="Yes to prompts (auto delete archive contents)")
    args = parser.parse_args()
    cpuc = psutil.cpu_count() #number of threads
    #max_threads = int(cpuc/2)
    max_threads = cpuc
    if max_threads < 1:
        max_threads = 1
    files = [os.path.abspath(os.path.join(args.dir,f)) for f in os.listdir(args.dir) if os.path.isfile(os.path.join(args.dir,f))]
    
    count = 0
    for i in range(max_threads):
        thread_library.append([])
    for file_name in files:
        thread_library[count].append(file_name)
        count+=1
        count%=max_threads
    for thread in thread_library:
        
        p = Process(target=ingest_file,args = (args.yes,thread,os.path.abspath(args.tmp),args.instrument))
        p.start()
        threads.append(p)
    for t in threads:
        t.join()
    
    
    
