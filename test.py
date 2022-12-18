import OrbaPreset
import xmltodict
import json
#import logging 

 
orba_preset =  OrbaPreset.PresetEntry()
orba_preset.load_from_file("artipreset/PanDrum_ea820c2d9ccd0e195b6e716bbc2e3a65.artipreset")

print ("-----------------------------")

#print (orba_preset.get_as_xml())
orba_preset.export_as_xml("test.xml")

print(json.dumps(orba_preset.get_as_dict(), indent=2))





         
#for i in  orba_preset.sound_preset.sample_set.sampled_sound:
  #  print(i.file_name  )




print(orba_preset.name)
print(orba_preset.sound_preset.synth_patch.mod_source1_1_destination)
print(orba_preset.sound_preset.sample_set.name)
print(orba_preset.sound_preset.sample_set.velocity_thresholds)
print(orba_preset.sound_preset.sample_set.note_thresholds) 

 
#print(orba_preset.sound_preset.sample_set.sampled_sound[0].get_as_dict())
print(orba_preset.modifier_chain.get_as_dict())



#print(xmltodict.unparse({"root":orba_preset.get_as_dict()}))


