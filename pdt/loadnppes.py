#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4
# Written by Alan Viars - This software is public domain

from bs4 import BeautifulSoup
import urllib2
import re, glob, sys
from subprocess import call

def do_update(process_full=True, download=True):
    months = ["January","Feburary","March","April", "May", "June"]
    #Get just the html page
    html_page = urllib2.urlopen("http://nppes.viva-it.com/NPI_Files.html")
    soup = BeautifulSoup(html_page)
    month =""
    year="2015"
    #get all links
    zipfilelinks = []
    for link in soup.findAll('a'):
        #print link
        #get just zips
        if link.get('href', "").endswith(".zip"):
            zipfilelinks.append(link.get('href', ""))
    
    #determine full v/s weekly
    weeklylinks = []
    full_link =""
    for link in zipfilelinks:

        for m in months:
            if link.__contains__(m):
                full_link = link
                month = m
        if link.__contains__("Report"):
            deactivation_link = link
        else:
            weeklylinks.append(link)
                    
            
    #Download full file
    if process_full:
        print 
        if download:
            print "Downloading", full_link        
            call(["wget", full_link])
        
        #Get filename and unzip
        filename = full_link.split("/")
        zipfilename = filename[-1]
        print "Unzip", zipfilename
       
        call(["unzip",zipfilename])
        
        #inspect the local directory for the CSV
        csv_files = glob.glob("*.csv")
        
        for f in csv_files:
            if f.__contains__("Header"):
                header_file = f
            else:
                main_file_to_import = f
        
        #Now import the file
        print "Import", main_file_to_import
        #first convert to json
        json_output_dir = "json-output"
        call(["csv2pjson-public.py", main_file_to_import, json_output_dir ])
        #now upload to mongo
        call(["jsondir2mongo", json_output_dir, "nppes", "pjson", "T", "127.0.0.1", "27017" ])
    
    
        #now create indexes
        call(["create-provider-indexes", "nppes", "pjson", "127.0.0.1", "27017", "Y" ])
    #Download weekly files
        #for link in weeklylinks:
        #    print "weekly", link        


if __name__ == "__main__":
    
    
    if len(sys.argv)!=3:
        print "Usage:"
        print "loadnppes.py [PROCESS_FULL Y/N] [DOWNLOAD_FROM_PUBLIC_FILE Y/N]"
        print "Example:"
        print "loadnppes.py Y Y"
        sys.exit(1)

    if sys.argv[1] in ("Y", "y", "T", True):
        process_full = True
    else:
        process_full = False
    
    if sys.argv[2] in ("Y", "y", "T", True):
        download = True
    else:
        download = False
    
    #Get the file from the command line
    do_update(process_full, download)