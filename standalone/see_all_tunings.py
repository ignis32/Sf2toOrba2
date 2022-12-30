 
import os
import glob
from os.path import exists

if not exists("OrbaPreset/OrbaPreset.py"):
    os.chdir("standalone") 

import OrbaPreset.OrbaPreset as OrbaPreset


file_list = glob.glob('artipreset/Drum/*.artipreset')

 



 	

for i in file_list:
    print(i)
    try:
        orba_preset =  OrbaPreset.PresetEntry()
        orba_preset.load_from_file(i)
        print ("..........")
        #print (i)
        print (f"{orba_preset.mode} {orba_preset.name}")
   
        
        print( f"sampledrumpatches: { len  (orba_preset.sound_preset.kit_patch.sample_drum_patch)} "   )
        print( f"sampledsounds: { len  (orba_preset.sound_preset.sample_set.sampled_sound)} "   )

        
        for i in orba_preset.sound_preset.kit_patch.drum_patch:
            print(f"DrumPatch: index {i.index} note {i.note}  midinote {i.midiNote}")
        
        for i in orba_preset.sound_preset.kit_patch.cymbal_patch:
            try: 
                note = i.note
            except:
                note = "n/a"

            print(f"CymbalPatch: index {i.index} note {note}  midinote {i.midiNote}")

        
        print(f"ShakerPatch: index {orba_preset.sound_preset.kit_patch.shaker_patch.index}   midinote {orba_preset.sound_preset.kit_patch.shaker_patch.midiNote}")
 
    

        for i in orba_preset.sound_preset.kit_patch.sample_drum_patch:
            print(f"SampleDrumPatch: index {i.index} note {i.note}  midinote {i.midiNote}")


        print ( f"note_th: {orba_preset.sound_preset.sample_set.noteThresholds}  :amount {len( orba_preset.sound_preset.sample_set.noteThresholds.split(',') )}")
        print ( f"vel_th: {orba_preset.sound_preset.sample_set.velocityThresholds}  :{ orba_preset.sound_preset.sample_set.velocityThresholds.count(']') }")
        print ( f"samplemap: {orba_preset.sound_preset.sample_set.sampleMap}  :{orba_preset.sound_preset.sample_set.sampleMap.count(']')}  ")
        print ( f"tuning: {orba_preset.tuning_entry.tuning}   : {   len(  orba_preset.tuning_entry.tuning.split(',')  )  }")
        
        print ( f"samples: {len(orba_preset.sound_preset.sample_set.sampled_sound)} ")

        
        # print (".")
        # print (  )
    except Exception as e:
       print ("nah")
       print (e)
       pass

 
 