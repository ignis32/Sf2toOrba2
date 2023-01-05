
import config_convertor
import sf2_stuff
import OrbaPreset.OrbaPreset as OrbaPreset
import os
from os.path import exists
import helpers
import shutil

if not exists("OrbaPreset/OrbaPreset.py"):
    os.chdir("standalone")

 
#------ omg garbage to refactor

def get_template_mode():
        preset = OrbaPreset.PresetEntry() 
        preset.load_from_file(config_convertor.template_file)
        return preset.mode


def add_image_to_preset(preset):

        ## create some  stub png image
        image_folder_path=f"{config_convertor.target_dir}/{ preset.name}/Common/Images"
        image_filename=f"{  preset.name }_{ helpers.md5sum(  preset.name + 'image' )  }.png"
        image_file_path= f"{image_folder_path}/{image_filename}"     
        helpers.ensure_folder(image_folder_path)
        shutil.copyfile("sf2toorba.png", image_file_path)
        return image_filename


def generate_OrbaPreset(raw_instrument_name) -> OrbaPreset.PresetEntry:
        print("loading template artipreset {template_file}")
        preset = OrbaPreset.PresetEntry() 
        preset.load_from_file(config_convertor.template_file)
        template_name = preset.name

        preset.factory=0   #!!! vital to be able to remove custom preset later properly
        preset.readOnly=0  #!!! vital to be able to remove custom preset later properly.
        
        preset.name =f"SF2_{config_convertor.sf2_filename}_{helpers.slugify_name(raw_instrument_name)}_{preset.mode}"
        preset.uuid = helpers.md5sum(preset.name) 
        preset.sound_preset.name =   preset.name
        preset.sound_preset.sample_set.name =  preset.name
        preset.description = f"Generated with Sf2toOrba2 from SF2 [{config_convertor.sf2_filename}]:[{raw_instrument_name}] using  [{preset.mode}] artipreset template  [{template_name}]"
        preset.tagList = "#sf2 #converted"
        preset.artist = "SF2toOrba2"
        preset.visuals.cover_art.artist = "SF2toOrba2"
        preset.visuals.cover_art.coverImageRef = "stub"
        return preset


#------
    

#
try:  # whatever happens, we should remove goddamn temp files

    mode = get_template_mode()  # read template first time and lookup the mode.
    sf2o2_instruments = sf2_stuff.load_sf2o2_instruments(mode=mode)
    print("-------------------------------------------")
    print("loading complete")

    for sf2o2instrument in  sf2o2_instruments:
  
        # load template artipreset and fill some basic fields. More complex stuff will be modifed later.
        # create stub png picture
        preset = generate_OrbaPreset(sf2o2instrument.slug_name)

        #generate stub image and add it to preset
        image_filename=add_image_to_preset(preset)  # and create the image file
        preset.visuals.cover_art.coverImageRef = image_filename



        # generate sampledsounds, export samples to output and attach them to preset.
        sampled_sounds = []
        for s in sf2o2instrument.sf2o2_samples:
            sampled_sound =  OrbaPreset.SampledSound(s.generate_sampled_sound_dict(sf2o2instrument.slug_name, mode)) 
            sampled_sound.subdirectory = preset.name  #ugly spaghetti here. need to fix.
            # export samples stored and temp files
            sample_folder_path=f"{config_convertor.target_dir}/{preset.name}/Common/SamplePools/User/{preset.name}"
            helpers.ensure_folder(sample_folder_path)
            print (sampled_sound.get_as_xml())
            shutil.copy2(s.tmp_wav_file , f"{sample_folder_path}/{sampled_sound.fileName}")
            
            if mode == "Drums":
                sampled_sound.pitch =  round (-(48000 / s.sample_rate) , 6)
            sampled_sounds.append(sampled_sound)
        preset.sound_preset.sample_set.sampled_sound = sampled_sounds


        preset.sound_preset.sample_set.noteThresholds = sf2o2instrument.note_thresholds
        preset.sound_preset.sample_set.velocityThresholds = sf2o2instrument.velocity_thresholds
        preset.sound_preset.sample_set.sampleMap = sf2o2instrument.sample_mappings
     


        #TBA add kitpatch stuff for DRUM MODE
        if mode == "Drums":
            del preset.sound_preset.kit_patch.cymbal_patch
            del preset.sound_preset.kit_patch.drum_patch
            del preset.sound_preset.kit_patch.shaker_patch

            preset.sound_preset.kit_patch.sample_drum_patch = []
            preset.sound_preset.kit_patch.compatibility.numCymbals=0
            preset.sound_preset.kit_patch.compatibility.numDrums=0
            preset.sound_preset.kit_patch.compatibility.numShakers=0

            preset.sound_preset.kit_patch.compatibility.numSampleDrums =   len(sf2o2instrument.velocity_thresholds_list)
    

            #generate sampledrumpatches, we expect that each playable note is mentioned in note thresholds already

            for idx, keytop in  enumerate(sf2o2instrument.note_thresholds_list):

                #TBA this data should be better, now it is something generic
                data ={'@index': idx, 
                '@drumMode': '0', '@ampVelocity': '200', 
                '@snapVelocity': '0', '@snapLevel': '0', '@snapColor': '0', 
                '@bendVelocity': '0',  '@bendDepth': '0', '@bendTime': '0', 
                '@gainRampStart': '0', '@gainRampEnd': '0', '@gainRampTime': '0', 
                '@clipRampStart': '74', '@clipRampEnd': '56', '@clipRampTime': '0', 
                '@fwRampStart': '0', '@fwRampEnd': '0', '@fwRampTime': '0', 
                '@decayRelease': '63', '@decayHold': '255', '@flamCount': '0', '@flamRate': '0', 
                '@level': '255', '@pan': '0', 
                '@tailLevel': '41', '@tailDelay': '0', '@tailDecay': '23', '@fx': '0', 
                '@note': '0', '@midiNote': keytop, '@priority': idx}


                sample_drum_patch = OrbaPreset.SampleDrumPatch (data)
                preset.sound_preset.kit_patch.sample_drum_patch.append(sample_drum_patch)
                preset.tuning_entry.tuning="36,38,42,46,45,50,70,49"
        else:
            preset.tuning_entry.tuning = config_convertor.the_tunings[mode]['tuning']
            preset.tuning_entry.intervals = config_convertor.the_tunings[mode]['intervals']
            preset.tuning_entry.key = config_convertor.the_tunings[mode]['key']
            preset.tuning_entry.name = config_convertor.the_tunings[mode]['name']

            if mode =="Chords":
                preset.modifier_chain.modifier_entry.chord_modifier_params.minorChordList  =   config_convertor.the_tunings[mode]['chord_minor']
                preset.modifier_chain.modifier_entry.chord_modifier_params.majorChordList  =   config_convertor.the_tunings[mode]['chord_major']
                  
 


        #export artipreset   

        folder_mode = mode
        if mode == "Drums":
            folder_mode = "Drum"   # omg artiphon could not be consistent in the naming.
        if mode == "Chords":
            folder_mode = "Chord"  # omg artiphon could not be consistent in the naming.

        preset_folder_path=f"{config_convertor.target_dir}/{preset.name}/Common/Presets/{folder_mode}"          
        preset_file_name=f"{preset.name}_{preset.uuid}.artipreset"
        preset_file_path=f"{preset_folder_path}/{preset_file_name}"
        helpers.ensure_folder(preset_folder_path)
        preset.export_as_xml(preset_file_path)


        zip_folder = f"{config_convertor.target_dir}/{preset.name}"
        output_zip = f"{config_convertor.target_dir}/{preset.name}"
        #import shutil
        shutil.make_archive(output_zip, 'zip', zip_folder)
        


    sf2_stuff.clean_tmp()  
except Exception as e:
    sf2_stuff.clean_tmp()
    raise e

print(" ")
print (f"python orba_deploy_preset.py {output_zip}.zip" )
