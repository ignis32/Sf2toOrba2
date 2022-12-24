 
import os
import glob
from os.path import exists

if not exists("OrbaPreset/OrbaPreset.py"):
    os.chdir("standalone") 

import OrbaPreset.OrbaPreset as OrbaPreset





file_list = glob.glob('artipreset/*/*.artipreset')

for i in file_list:
    print ("..........")
    print(f"{i}")
    orba_preset =  OrbaPreset.PresetEntry()
    orba_preset.load_from_file(i)
    print (f"{orba_preset.mode} {orba_preset.name}")
    try:
        

        print (orba_preset.tuning_entry.tuning)
        print (orba_preset.tuning_entry.midiOctave)
        # print ( f"{orba_preset.sound_preset.sample_set.noteThresholds}  {len( orba_preset.sound_preset.sample_set.noteThresholds.split(',') )}")
        # print (".")
        # print ( orba_preset.sound_preset.sample_set.velocityThresholds)
        # print (".")
        # print ( orba_preset.sound_preset.sample_set.sampleMap)
        # print (".")
        # print ( len(orba_preset.sound_preset.sample_set.sampled_sound) )
    except:
        print ("nah")