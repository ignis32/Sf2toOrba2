import OrbaPreset.OrbaPreset as OrbaPreset
import xmltodict
import json
#import logging 
import glob
#import xmldiff
from lxml import etree
from xmldiff import main, formatting
import os

# this script is used to check if 
# 1) artipreset xml files would be LOGICALLY identical to original, after parsing it with OrbaPreset library and unparsed back
# 2) parsing/unparsing will cause an expection.


# testing difference manually:
# https://www.jsoftwarelabs.com/jslutils/xml-comparison


# vs code uses root folder of the project for runtime :*
os.chdir("standalone") 
print(os. getcwd() )
print("lets go")


# we are expecting artipreset folder to contain  Lead,Bass,Chord, Drum folders with artipreset files from Orba.
file_list = glob.glob('artipreset/*/*.artipreset')
 

for i in file_list:

    orba_preset =  OrbaPreset.PresetEntry()
    try:
        orba_preset.load_from_file(i)
        orba_preset.export_as_xml(str(i)+".reparsed")
        
        diff = main.diff_files(i, str(i)+".reparsed" )
        if diff != []:
                print("---------------")
                print(f"{i} {str(i)}.reparsed")
                print("---------------")
                print(diff)

    except Exception as e :
        print("!!!!!!!!!!!!!!!!!!!!")
        print(f"{i} {str(i)}.reparsed")
        print("---------------")
        print(e)
        #
        raise
         

  