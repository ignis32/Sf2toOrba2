 
import os
import glob
from os.path import exists

if not exists("OrbaPreset/OrbaPreset.py"):
    os.chdir("standalone") 

import OrbaPreset.OrbaPreset as OrbaPreset


file_list = glob.glob('artipreset/*/*.artipreset')
# for a in file_list:
#     print(a)
#     mode_folder = a.split( "\\")[1]
    
#     print(mode_folder)
# exit()
import helpers
import json
# identify collections
 
unique_tunings={}
unique_tunings['Lead']={}
unique_tunings['Bass']={}
unique_tunings['Chords']={}
unique_tunings['Drums']={}


sorted_stuff={}
for i in file_list:
   # print(i)
        orba_preset =  OrbaPreset.PresetEntry()
        orba_preset.load_from_file(i)
       # print (orba_preset.name)
        if orba_preset.mode == "Drums":
            continue
        
        if "stemArtist" in orba_preset.__dict__:
             continue


        if not  orba_preset.name in  sorted_stuff  :
                sorted_stuff[orba_preset.name] ={}
        print("!!!!!!!!!")
        print (orba_preset.modifier_chain.modifier_entry.chord_modifier_params if "modifier_entry" in  orba_preset.modifier_chain.__dict__ else "n/a")
        sorted_stuff[orba_preset.name][orba_preset.mode] =  {
                                "tuning": orba_preset.tuning_entry.tuning,
                                 "intervals": orba_preset.tuning_entry.intervals,
                                 "key": orba_preset.tuning_entry.key, 
                                 "chord_minor": orba_preset.modifier_chain.modifier_entry.chord_modifier_params.minorChordList if "modifier_entry" in  orba_preset.modifier_chain.__dict__ else "n/a",
                                 "chord_major": orba_preset.modifier_chain.modifier_entry.chord_modifier_params.majorChordList if "modifier_entry" in  orba_preset.modifier_chain.__dict__ else "n/a",
                
                                 "name":  orba_preset.tuning_entry.name,
                                }
        
unique_tuning_collection={}
for i in sorted_stuff:
    if len(sorted_stuff[i] ) == 3:
         
        uniq_hash = helpers.md5sum( json.dumps (sorted_stuff[i]))
        #print (uniq_hash)
        unique_tuning_collection[uniq_hash] = sorted_stuff[i]
    
print (unique_tuning_collection)
# for i in unique_tuning_collection:
#     print(i,flush=True)
#     print(json.dumps(unique_tuning_collection[i], indent=2), flush=True)
    
print(len(unique_tuning_collection))
exit()

for i in file_list:
   # print(i)



    try:
        orba_preset =  OrbaPreset.PresetEntry()
        orba_preset.load_from_file(i)
        mode = orba_preset.mode
        if not orba_preset.tuning_entry.tuning in unique_tunings[mode].keys():
            unique_tunings[mode][orba_preset.tuning_entry.tuning]=orba_preset.tuning_entry.intervals

        # print ("..........")
        # #print (i)
        # print (f"{orba_preset.mode} {orba_preset.name}")
   
        
       # print( f"sampledrumpatches: { len  (orba_preset.sound_preset.kit_patch.sample_drum_patch)} "   )
        # print( f"sampledsounds: { len  (orba_preset.sound_preset.sample_set.sampled_sound)} "   )

        
        # for i in orba_preset.sound_preset.kit_patch.drum_patch:
        #     print(f"DrumPatch: index {i.index} note {i.note}  midinote {i.midiNote}")
        
        # for i in orba_preset.sound_preset.kit_patch.cymbal_patch:
        #     try: 
        #         note = i.note
        #     except:
        #         note = "n/a"

        #     print(f"CymbalPatch: index {i.index} note {note}  midinote {i.midiNote}")

        
        # print(f"ShakerPatch: index {orba_preset.sound_preset.kit_patch.shaker_patch.index}   midinote {orba_preset.sound_preset.kit_patch.shaker_patch.midiNote}")
 
    

        # for i in orba_preset.sound_preset.kit_patch.sample_drum_patch:
        #     print(f"SampleDrumPatch: index {i.index} note {i.note}  midinote {i.midiNote}")


        # print ( f"note_th: {orba_preset.sound_preset.sample_set.noteThresholds}  :amount {len( orba_preset.sound_preset.sample_set.noteThresholds.split(',') )}")
        # print ( f"vel_th: {orba_preset.sound_preset.sample_set.velocityThresholds}  :{ orba_preset.sound_preset.sample_set.velocityThresholds.count(']') }")
        # print ( f"samplemap: {orba_preset.sound_preset.sample_set.sampleMap}  :{orba_preset.sound_preset.sample_set.sampleMap.count(']')}  ")
        #print ( f"tuning: {orba_preset.tuning_entry.tuning}   : { orba_preset.tuning_entry.key }  :{ orba_preset.tuning_entry.type }")
       # print ( f"tuning: {orba_preset.tuning_entry.intervals}  ")
        print ( f"tuning: {orba_preset.tuning_entry.key}  {orba_preset.tuning_entry.name}  ")
     
        # print ( f"samples: {len(orba_preset.sound_preset.sample_set.sampled_sound)} ")

        
        # print (".")
        # print (  )
    except Exception as e:
       print ("nah")
       print (e)
       pass

 
import json

print ("", flush=True)
print (json.dumps(unique_tunings, indent= 2))