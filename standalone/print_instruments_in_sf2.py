
from sf2utils.sf2parse import Sf2Instrument
from sf2utils.sf2parse import Sf2File
from sf2utils.generator import Sf2Gen
from sf2utils.bag import Sf2Bag
from sf2utils.sample import Sf2Sample
import config_convertor
import os
from os.path import exists

if not exists("OrbaPreset/OrbaPreset.py"):
    os.chdir("standalone")


sf2_filepath = f"{config_convertor.sf2_folder_path}/{config_convertor.sf2_filename}"
sf2_file = open(sf2_filepath, "rb")  # We need this file to be opened until the end of the script, or sample exporting will not work (after closing the handler)
#with open(sf2_filepath, 'rb') as sf2_file:    
sf2 = Sf2File(sf2_file)
 

for instrument in sf2.instruments:
    print (instrument.name)