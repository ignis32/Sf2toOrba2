import OrbaPreset
import xmltodict
import json
#import logging 
import glob

# testing difference with
# https://www.jsoftwarelabs.com/jslutils/xml-comparison


# file_list = glob.glob('artipreset/*/*.artipreset')

# print (file_list)

# for i in file_list:
#     print("---------------")
#     print(i)
#     orba_preset =  OrbaPreset.PresetEntry()
#     try:
#         orba_preset.load_from_file(i)
#      #   orba_preset.export_as_xml(str(i)+".reparsed")
#     except:
#         print("---------------")
#         print(i)
#         raise



orba_preset =  OrbaPreset.PresetEntry()
#orba_preset.load_from_file("artipreset/Custom/PanDrum_ea820c2d9ccd0e195b6e716bbc2e3a65.artipreset")
#orba_preset.load_from_file("artipreset/Chord/1981_ca0f71882db74f11a2ac6a25c418b841.artipreset")
#orba_preset.load_from_file("artipreset/Lead/GrandPianoLead_da108650b6004591ab378e06b3a31c6b.artipreset")

orba_preset.load_from_file("artipreset/Drum/Dragonfruit_8221dd734c3046af9f15f685441d8735.artipreset")
print ("-----------------------------")

#print (orba_preset.get_as_xml())
orba_preset.export_as_xml("test.xml")



 

#print(json.dumps(orba_preset.get_as_dict(), indent=2))





# #for i in  orba_preset.sound_preset.sample_set.sampled_sound:
#   #  print(i.file_name  )




print(orba_preset.name)
#print(orba_preset.sound_preset.sample_set)
print(orba_preset.sound_preset.sample_set.name)
print(orba_preset.sound_preset.sample_set.velocityThresholds)
print(orba_preset.sound_preset.sample_set.noteThresholds) 

 
# #print(orba_preset.sound_preset.sample_set.sampled_sound[0].get_as_dict())
# print(orba_preset.modifier_chain.get_as_dict())



# #print(xmltodict.unparse({"root":orba_preset.get_as_dict()}))


