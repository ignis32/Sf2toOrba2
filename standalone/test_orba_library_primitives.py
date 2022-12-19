import OrbaPreset.OrbaPreset as OrbaPreset
import xmltodict
import json
#import logging 
import glob
#import xmldiff
from lxml import etree
from xmldiff import main, formatting
import os
from os.path import exists

# VSCode uses root folder of the project as a context to run the script, and it fails without changing folder  manually
if not exists("OrbaPreset/OrbaPreset.py"):
    os.chdir("standalone") 

    
# just to show some object manipulations 

orba_preset =  OrbaPreset.PresetEntry()
orba_preset.load_from_file("artipreset/Custom/PanDrum_ea820c2d9ccd0e195b6e716bbc2e3a65.artipreset")
# orba_preset.load_from_file("artipreset/Chord/1981_ca0f71882db74f11a2ac6a25c418b841.artipreset")
# orba_preset.load_from_file("artipreset/Lead/GrandPianoLead_da108650b6004591ab378e06b3a31c6b.artipreset")
# orba_preset.load_from_file("artipreset/Chord/SoulChords_bda2c9d112a64a3ab24f42ea99c58648.artipreset.reparsed")
# orba_preset.load_from_file("artipreset/Drum/Dragonfruit_8221dd734c3046af9f15f685441d8735.artipreset")




# print ("-----------------------------")
#print (orba_preset.get_as_xml())
#orba_preset.export_as_xml("test.xml")
#print(json.dumps(orba_preset.get_as_dict(), indent=2))





for i in  orba_preset.sound_preset.sample_set.sampled_sound:
   print(i.fileName  )


print(orba_preset.name)
print(orba_preset.description)
print(orba_preset.tagList)
print(orba_preset.sound_preset.sample_set.name)
print(orba_preset.sound_preset.sample_set.velocityThresholds)
print(orba_preset.sound_preset.sample_set.noteThresholds) 


# 
# #print(orba_preset.sound_preset.sample_set)
print(orba_preset.sound_preset.sample_set.sampled_sound[0].pitch)
# print(orba_preset.modifier_chain.get_as_dict())
# #print(xmltodict.unparse({"root":orba_preset.get_as_dict()}))


