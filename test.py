import OrbaPreset
import xmltodict
import json
#import logging 

 
orba_preset =  OrbaPreset.PresetEntry()
orba_preset.load_from_file("artipreset/PanDrum_ea820c2d9ccd0e195b6e716bbc2e3a65.artipreset")

print ("-----------------------------")

#with open("PanDrum_ea820c2d9ccd0e195b6e716bbc2e3a65.artipreset") as fd:
#           print( json.dumps( xmltodict.parse(fd.read())['PresetEntry']))
         
for i in  orba_preset.sound_preset.sample_set.sampled_sound:
    print(i.file_name  )


print(orba_preset.name)
print(orba_preset.sound_preset.synth_patch.mod_source1_1_destination)
print(orba_preset.sound_preset.sample_set.name)
print(orba_preset.sound_preset.sample_set.velocity_thresholds)
print(orba_preset.sound_preset.sample_set.note_thresholds)