 
import os
import glob
from os.path import exists

if not exists("OrbaPreset/OrbaPreset.py"):
    os.chdir("standalone") 

import OrbaPreset.OrbaPreset as OrbaPreset


file_list = glob.glob('artipreset/Drum/*.artipreset')



attribs= ["index", "drumMode", "ampVelocity", "snapVelocity", "snapLevel", "snapColor", "bendVelocity", "bendDepth",
 "bendTime", "gainRampStart", "gainRampEnd", "gainRampTime", "clipRampStart", "clipRampEnd","clipRampTime",
  "fwRampStart", "fwRampEnd", "fwRampTime", "decayRelease", "decayHold", "flamCount", "flamRate",
"level", "pan", "tailLevel", "tailDelay", "tailDecay", "fx", "note", "midiNote", "priority"]

stats={}

for a in attribs:
    stats[a] = {"variants":[], "minval":9999, "maxval":0 }



for i in file_list:
    print(i)
    orba_preset =  OrbaPreset.PresetEntry()
    orba_preset.load_from_file(i)
    # print ("..........")
    # print (i)
    # print (f"{orba_preset.mode} {orba_preset.name}")
  
    try:
       

        for ii in orba_preset.sound_preset.kit_patch.sample_drum_patch:
         try:
            for attrib in ii.__dict__:

                stats[attrib]["variants"].append(   int( getattr(ii, attrib))   )
                stats[attrib]["minval"] = min  (int(getattr(ii, attrib)) , stats[attrib]["minval"])

                stats[attrib]["maxval"] = max  (int(getattr(ii, attrib)) ,stats[attrib]["maxval"] )
         except Exception as e:
            print(e)
 
         
         
    except Exception as e:
       print ("nah")
       print (e)
       pass

for i in stats.keys():
    #print (i)
    summ = sum (stats[i]['variants'])
    avg =  summ / len(stats[i]['variants'])
    stats[i]['avg']=avg
import json
#print(json.dumps(stats, indent= 2))

for i in stats.keys():

    print(f"[{i}]")
    print (f"known values from {stats[i]['minval']} to {stats[i]['maxval']}, avg value: {stats[i]['avg']}")
 