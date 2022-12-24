
# # https://daizyu.com/posts/2021-09-11-001/

# # https://freepats.zenvoid.org/sf2/sfspec24.pdf

# # https://pjb.com.au/midi/sfspec21.html#6.2
import time
import os
from sf2utils.sf2parse import Sf2Instrument
from sf2utils.sf2parse import Sf2File
from sf2utils.generator import Sf2Gen
import hashlib
import slugify #  install as  python-slugify  (regular slugify is something outdated)
import pprint
import OrbaPreset.OrbaPreset as OrbaPreset
import shutil
import itertools
import tempfile
import pydub
from pydub import AudioSegment
import math
# There is no strict assignment of the note 60 to certain octave. 
# https://petervodden.blog/portfolio/middle-c-c3-or-c4/
# note 60 can be C3 or C4 or even sometimes C5 depending on interpretation.
# goddamn standards cannot even agree on what the 60 note is. 
from os.path import exists

import logging
logging.disable(logging.WARNING)


# Most popular
MIDDLE_C_IS_C5 =  0
MIDDLE_C_IS_C4 = -1   
MIDDLE_C_IS_C3 = -2  


# input parameters. TBA - implement as command line arguments


OCTAVE_SHIFT= MIDDLE_C_IS_C5    #override this if samples pitch is wrong.

template_file = "artipreset/Lead/PanDrum_ea820c2d9ccd0e195b6e716bbc2e3a65.artipreset"
#template_file = "artipreset/Drum/JiveKit_e53cec68aa6340e1b1bfa4491b7efe22.artipreset"
sf2_folder_path='test_sf2'

#sf2_filename = r'(130 sounds) 27mg_Symphony_Hall_Bank.SF2'
#sf2_filename = r'ACCORDION.sf2'
#sf2_filename = r'Hang-D-minor-20220330.sf2'
#sf2_filename = r'314-Good_Rocky_Drum.sf2'
sf2_filename = r'Marimbala.sf2'




target_dir = r'output'



sf2_filepath = f"{sf2_folder_path}/{sf2_filename}"

#  just a workround for my VScode folder context
if not exists("OrbaPreset/OrbaPreset.py"):
    os.chdir("standalone") 


temp_files_to_remove=[]

def note_to_text(number: int):
    NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    NOTES_IN_OCTAVE = len(NOTES)
    octave = number // NOTES_IN_OCTAVE
    note = NOTES[number % NOTES_IN_OCTAVE]
    return f"{note}{octave+OCTAVE_SHIFT}"    # with  OCTAVE_SHIFT=0 it will use C5 as middle C.
 
def md5sum(text):
    source = text.encode()
    md5 = hashlib.md5(source).hexdigest() # returns a str
    return (md5)

def ensure_folder(path):
    # ensure folder
    try:
        os.makedirs(path)
    except FileExistsError:
    # directory already exists
        pass

def note_to_pitch(midi_note, fine_tuning_cents = 0 , coarse_tuning_semitones = 0, sample_rate = 48000, midi_key_pitch_influence = 0):
  
    print(f"note {midi_note } sample rate {sample_rate}  fine {fine_tuning_cents} coarse {coarse_tuning_semitones} ")
    # orba uses 48000 sample rate, and every other sample rate should be tuned accordingly
    sample_rate_pitch_correction = 48000/sample_rate  # sample rate correction
    octave_shift_notes = 12*(OCTAVE_SHIFT+1)

    # pitch calculation  [if 48000, changes nothing ] [note A freq]   [A above Midle C] [middle C definition] [bag coarse tuning]   [not sure about math here, but one semitone is 100 cents]
    if  midi_key_pitch_influence != 0  :  
       
       
        pitch_with_no_sample_rate_correction = 440.0 * pow(2, (midi_note-69   - coarse_tuning_semitones - (fine_tuning_cents/100)   )/12)
       
       
        print (f"  non corrected pitch {pitch_with_no_sample_rate_correction}")
        pitch =   sample_rate_pitch_correction * pitch_with_no_sample_rate_correction
        print (f"  corrected pitch {pitch}")
    else:
        pitch = sample_rate_pitch_correction * -1  # this means pitch is static and not transposed by orba depending on note. Only sample rate correction.
        print (f"static pitch {pitch}")
    return  pitch
                          #
def note_to_pitch_old(midi_note, fine_tuning_cents = 0 , coarse_tuning_semitones = 0, sample_rate = 48000, midi_key_pitch_influence = 0):
  
    print(f"note {midi_note } sample rate {sample_rate}  fine {fine_tuning_cents} coarse {coarse_tuning_semitones} ")
    # orba uses 48000 sample rate, and every other sample rate should be tuned accordingly
    sample_rate_pitch_correction = 48000/sample_rate  # sample rate correction
    octave_shift_notes = 12*(OCTAVE_SHIFT+1)

    # pitch calculation  [if 48000, changes nothing ] [note A freq]   [A above Midle C] [middle C definition] [bag coarse tuning]   [not sure about math here, but one semitone is 100 cents]
    if  midi_key_pitch_influence != 0  :  
        pitch_with_no_sample_rate_correction = 440.0 * pow(2, (midi_note-69  + octave_shift_notes - coarse_tuning_semitones - (fine_tuning_cents/100)   )/12)
        print (f"  non corrected pitch {pitch_with_no_sample_rate_correction}")
        pitch =   sample_rate_pitch_correction * pitch_with_no_sample_rate_correction
        print (f"  corrected pitch {pitch}")
    else:
        pitch = sample_rate_pitch_correction * -1  # this means pitch is static and not transposed by orba depending on note. Only sample rate correction.
        print (f"static pitch {pitch}")
    return  pitch

 

def create_temp_wav_file(name):
    
    tmp_wav_file = tempfile.NamedTemporaryFile(prefix = f"sf2toOrba2.{name}.", suffix= ".tmp.wav",delete=False)  
    temp_files_to_remove.append(tmp_wav_file.name)  # remember all the temporary files to remove them before ending script.
    tmp_wav_file.close()
    return tmp_wav_file
 


def parse_instrument_samples(instrument: Sf2Instrument ):
    
    if  instrument.name  == "EOI":  # this is not a real instrument, "EOI" indicating end of instruments.
        return  []   
        
    print (f"Instrument: { instrument.name} #{instrument.bag_size}     {instrument.bag_idx}")
    
    # bag - A SoundFont data structure element containing a list of preset zones or instrument zones
    # instrument zone - A subset of an instrument containing a sample reference and associated articulation data defined to play over certain key numbers and velocities.
    # preset zone - A subset of a preset containing an instrument reference and associated articulation data defined to play over certain key numbers and velocities.
 
    parsed_instrument_samples=[]
    
    sample_index = 0
    for bag in instrument.bags:
        if  (bag.sample) == None:
            print("no sample bag")  # I am not sure why these appear in bags, but whatever. most probably is has something to do with global zones.
            print("=======================")

            continue
         
        allowed_pattern=r'[^-a-zA-Z0-9_#()]+' 
        instrument_name = "SF2_"+slugify.slugify(instrument.name, regex_pattern=allowed_pattern, lowercase=False)  # this name is used as a folder name, it should be valid for filesystem
        
        if bag.sample.pitch_correction !=0:
            print(f"pitch correction found for sample {bag.sample.name}:  {bag.sample.pitch_correction}") 
            raise ValueError("sample pitch correction is not implemented, byte chPitchCorrection")
            #return  []

        

        key_range_top = bag.key_range[-1] if bag.key_range != None else 127         #  root note for the sample  can be defined in bag, or fallback to the information in sample itsef  
        
        root_note = bag.base_note if bag.base_note != None  else (bag.sample.original_pitch)
        print (f"root note: {root_note}")
        root_note = key_range_top if bag.midi_key_pitch_influence == 0 else root_note    
        print (f"root note (midi key pitch influence override): {root_note}")
      
        sample_name = slugify.slugify(bag.sample.name,regex_pattern=allowed_pattern, lowercase=False, ) #.replace(" ","_")
        sample_uuid = md5sum ( f"{instrument_name}_{sample_name}_{note_to_text(root_note)}" )
        filename =             f"{instrument_name}_{sample_name}_{note_to_text(root_note)}_{sample_uuid}.wav"

        coarse_tuning_semitones  = bag.tuning  if bag.tuning != None else 0
        fine_tuning_cents   =  bag.fine_tuning if bag.fine_tuning != None else 0
        
        
        # in drum instruments it could be that pitch is set almost randomly, but wav sample is not modified on playback, as no transpose is supposed
        # We emulate it in orba by setting pitch to -1, and try to guess the note from key range.
        print(f"calculating pitch for {sample_name}")
        pitch = note_to_pitch(root_note, coarse_tuning_semitones= coarse_tuning_semitones, fine_tuning_cents=fine_tuning_cents, sample_rate = bag.sample.sample_rate, midi_key_pitch_influence = bag.midi_key_pitch_influence)  
        
    


        # exporting sample to temporary file
        tmp_wav_file = create_temp_wav_file(sample_name)
        bag.sample.export(tmp_wav_file.name)

         
        # this dict that will be used to create SampledSound class, that represents SampledSound element in xml.
        SampledSoundDict = {   

             #  the only data required for SampledSound xml part generation, they will go directy to xml later
                '@sampleIndex':   sample_index,
                '@name':          sample_name,
                '@loopStart':     bag.cooked_loop_start if bag.sample_loop !=None and bag.sample_loop !=False else 0, # if there is no loop, in orba it means 0 for both start and end
                '@loopEnd':       bag.cooked_loop_end   if bag.sample_loop !=None and bag.sample_loop !=False else 0,
                '@pitch':         pitch ,
                '@fileName':      filename,
                '@subdirectory':  instrument_name,
                '@pool': "User",

            #  auxilary attributes that do not exist in xml but required for doing stuff outside of SampledSound elements.
            #  attributes starting with aux_  will not be exported to xml
                '@aux_key_range':       bag.key_range,
                '@aux_key_range_top':   key_range_top,
                '@aux_velocity_range':  bag.velocity_range,
                '@aux_velocity_range_top': bag.velocity_range[-1] if bag.velocity_range != None and bag.velocity_range != False else 127,

                '@aux_instrument_name' : instrument_name,
                '@aux_TMP_WAV_FILE': tmp_wav_file,
                '@aux_pan': bag.pan        
        }

        sample_index += 1
        parsed_instrument_samples.append(SampledSoundDict)

    return parsed_instrument_samples


def parse_instrument_metadata(instrument):
    instrument_metadata = { 
        'instrument_name':   "SF2_"+slugify.slugify(instrument.name, lowercase=False) ,
        'instrument_uuid': md5sum("SF2_"+slugify.slugify(instrument.name, lowercase=False) )  
    }
     
    return instrument_metadata





def add_image_to_preset(instrument_metadata):

        ## create some  stub png image
        image_folder_path=f"{target_dir}/{instrument_metadata['instrument_name']}/Common/Images"
        image_filename=f"{  instrument_metadata['instrument_name'] }_{ md5sum( instrument_metadata['instrument_name'] + 'image' )  }.png"
        image_file_path= f"{image_folder_path}/{image_filename}"     
        ensure_folder(image_folder_path)
        shutil.copyfile("sf2toorba.png", image_file_path)
        return image_filename

def generate_OrbaPreset(instrument_metadata):

        preset = OrbaPreset.PresetEntry() 
        preset.load_from_file(template_file)

        preset.factory=0   #!!! vital to be able to remove custom preset later properly
        preset.readOnly=0  #!!! vital to be able to remove custom preset later properly.
        preset.uuid = instrument_metadata ['instrument_uuid']
        template_name = preset.name
        preset.name = instrument_metadata['instrument_name']
        preset.sound_preset.name =  instrument_metadata['instrument_name']
        preset.sound_preset.sample_set.name = instrument_metadata['instrument_name']
        preset.description = f"Generated with Sf2toOrba2 from SF2 [{sf2_filename}] using artipreset template [{preset.mode}] [{template_name}]"
        preset.tagList = "#sf2 #converted"
        preset.artist = "SF2toOrba2"
        preset.visuals.cover_art.artist = "SF2toOrba2"
        preset.visuals.cover_art.coverImageRef = image_filename
        return preset


def generate_SampledSounds(instrument):
        parsed_instrument_samples  = parse_instrument_samples(instrument)     
        sampled_sounds = []
        
        for sampled_sound_data_plus_aux in parsed_instrument_samples:
            sampled_sound = OrbaPreset.SampledSound(sampled_sound_data_plus_aux) 
            sampled_sounds.append(sampled_sound)
        return sampled_sounds

def sort_sampled_sounds_by_key_and_velocity(sampled_sounds):
       #  by_key      = lambda x:   int(x.aux_key_range_top)   
       #  by_velocity = lambda x:   int(x.aux_velocity_range_top)   
        by_key_and_velocity     = lambda x:   ( int(x.aux_key_range_top), int(x.aux_velocity_range_top)   )
        sorted_sample_sounds = sorted(sampled_sounds, key=by_key_and_velocity)
        return sorted_sample_sounds

def  group_sampled_sounds_by_key_and_velocity(sorted_sampled_sounds):
    by_key_and_velocity     = lambda x:   ( int(x.aux_key_range_top), int(x.aux_velocity_range_top)   )
    return itertools.groupby(sorted_sampled_sounds, key = by_key_and_velocity)

def  group_sampled_sounds_by_key (sorted_sampled_sounds):
    by_key      = lambda x:   int(x.aux_key_range_top) 
    return itertools.groupby(sorted_sampled_sounds, key = by_key)

def  group_sampled_sounds_by_velocity(sorted_sampled_sounds):
    by_velocity = lambda x:   int(x.aux_velocity_range_top) 
    return itertools.groupby(sorted_sampled_sounds, key = by_velocity)

def determine_group_max_duration(group_list: list):

    max_duration = 0
    for s in group_list:
        wav = AudioSegment.from_wav(s.aux_TMP_WAV_FILE.name)
        
        max_duration = max(math.ceil(wav.duration_seconds*1000), max_duration)
        print(f"duration: {math.ceil(wav.duration_seconds*1000)}")

    return max_duration

def reindex(sorted_sample_sounds):

        idx=0
        for sample_sound in sorted_sample_sounds:
            sample_sound.sampleIndex = idx
            idx+=1


#mix all sampledsounds in the list into one 
def mix_sampled_sounds_group_list(group_list):

    print(f" max duration: {determine_group_max_duration(group_list)}")

    #create an empty audiosegment sound with duration as maximum duration among group.  (Overlay does not autoextend size of the mix, when mixing with a longer sample)
    mix = AudioSegment.silent(duration = determine_group_max_duration(group_list)).set_channels(2)

    for sampled_sound in group_list:
        # add all samples from the group into the mix, convert them to stereo and set pan as mentioned  in corresponding bags
        # ?? what will happen if same sample is used multiple times in different bags ??
        mix =  mix.overlay( AudioSegment.from_wav(sampled_sound.aux_TMP_WAV_FILE.name).set_channels(2).pan(  sampled_sound.aux_pan)  )

    tmp_wav_file = create_temp_wav_file("MIX_"+group_list[0].name)
     
    mix.export(tmp_wav_file.name, format="wav")
    print (tmp_wav_file.name)
    group_list[0].aux_TMP_WAV_FILE = tmp_wav_file
    group_list[0].name = "MIX_"+group_list[0].name
    group_list[0].fileName = "MIX_"+group_list[0].fileName
    return group_list[0]
       

def mix_sampled_sounds(grouped_sampled_sounds):

        sorted_sampled_sounds  = sort_sampled_sounds_by_key_and_velocity(sampled_sounds)
        grouped_sampled_sounds = group_sampled_sounds_by_key_and_velocity(sorted_sampled_sounds)

        mixed_sampled_sounds = []

        for key, group in  grouped_sampled_sounds:
  
             
            print("---group---")      
            # SF2 supports two  samples sounding in the same time. Orba - does not.
            group_list= list(group)  #group is an iterator, when we can use it only once, so let's convert it to list.
            
            if len(group_list)>1:
                print("Multiple samples with the same velocity and key detected. Trying to mix them together")

                mixed_sampled_sound = mix_sampled_sounds_group_list(group_list)
                mixed_sampled_sounds.append(mixed_sampled_sound)
            else:
                mixed_sampled_sounds.append(group_list[0])  # there is one sample anyway

        return mixed_sampled_sounds


def generateSampleSetMetadata(mixed_sampled_sounds):

    print("Generating SampleSet Metadata")
        
    # calculate note thresholds and sample mapping
    note_thresholds_list   = []
    sample_mappings_list   = []
    velocity_thresholds_list = []
    key_grouped_sampled_sounds = group_sampled_sounds_by_key(mixed_sampled_sounds)
    
    for key, group in  key_grouped_sampled_sounds:          
        print("---group---")    
        note_thresholds_list.append(str(key))

        group_sample_mapping = []
        group_velocity_threshold = []
        for i in group:
            group_sample_mapping.append(i.sampleIndex)
            group_velocity_threshold.append(i.aux_velocity_range_top)
        group_velocity_threshold.pop() # two samples for two rangers mean only one value in orba, last one is ommited. 
        sample_mappings_list.append(group_sample_mapping)
        velocity_thresholds_list.append(group_velocity_threshold)



    note_thresholds_list.pop() # note threshold always has one less element than mappings. (last one is ommited)

    note_thresholds=",".join(note_thresholds_list) # convert to single string
    sample_mappings  = str(sample_mappings_list)[1:-1].replace(" ", "")
    velocity_thresholds =  str(velocity_thresholds_list)[1:-1].replace(" ", "")

    

    print (f"note_thresholds:   {note_thresholds}    len:  { len(note_thresholds_list) }" )
    print (f"sample_mappings:   {sample_mappings}    len:  { len(sample_mappings_list) }" )
    print (f"velocity_thresholds: {velocity_thresholds}  len:  { len(velocity_thresholds_list) }" )

    if (len(note_thresholds_list) +1 )  ==  len(sample_mappings_list) == len(velocity_thresholds_list) :
        print("sanity check pass")
    else:
        raise ValueError("Something is wrong with thresholds and sample mapping")

    return note_thresholds, sample_mappings, velocity_thresholds


######-----------------------------------------------------------------

with open(sf2_filepath, 'rb') as sf2_file:
    
    #use sf2util library to parse sf2 bank
    sf2 = Sf2File(sf2_file)
    print ("\n\n\n")
    print (f"number of instruments in the sf2: {len(sf2.instruments)-1}")   #/// there is an additional EOI fake instrument in the end, marks end of instrument list
    
    # instrument - In the SoundFont standard, a collection of zones which represents the sound of a single musical instrument or sound effect set.
    # one sf2 file might contain multiple instruments.
    
    print ("----------------------------------------------------------------")
    
    for instrument in sf2.instruments:
        
        instrument_metadata = parse_instrument_metadata(instrument)
        

#### TEMPORARY
       # if instrument_metadata['instrument_name'] != 'SF2_CHURCH-ORGAN':
        if instrument_metadata['instrument_name'] in ['SF2_VIBRAPHONE','SF2_CELLO', 'SF2_Accordian'] :  ## excluding instruments with pitch corrected samples.
            continue
#### TEMPORARY

        #skip "fake"  sf2 instrument
        if instrument_metadata['instrument_name'] == 'SF2_EOI':
            continue
        
        # create stub png picture
        image_filename=add_image_to_preset(instrument_metadata)

        # load template artipreset and override some fields  with data from sf2 instrument
        preset = generate_OrbaPreset(instrument_metadata)

        ##   generate list of samples as SampledSound objects and fill them with metadata.
        sampled_sounds = generate_SampledSounds(instrument)
            

        # if there are samples that have the same key and velocity
        # (it it can happen in sf2, for example, when two mono samples with panning are used to
        # represent stero)
        # there is no way to express it in Orba2 terms, so we are just mixing them down according to
        # each sample's pan.

        # loop points could be broken though.

        #mix overlapping samples, and sort the by key and velocity
        mixed_sampled_sounds = mix_sampled_sounds(sampled_sounds)

        #some of samples had been removed, order has chnaged, we need to write indexes to samples once again
        reindex(mixed_sampled_sounds)

        # override all the calculated SampleSet parameters
        note_thresholds, sample_mappings, velocity_thresholds = generateSampleSetMetadata(mixed_sampled_sounds)

        preset.sound_preset.sample_set.sampled_sound = mixed_sampled_sounds
        preset.sound_preset.sample_set.noteThresholds = note_thresholds
        preset.sound_preset.sample_set.velocityThresholds = velocity_thresholds
        preset.sound_preset.sample_set.sampleMap = sample_mappings


        # export samples stored and temp files

        sample_folder_path=f"{target_dir}/{instrument_metadata['instrument_name']}/Common/SamplePools/User/{instrument_metadata['instrument_name']}"
        ensure_folder(sample_folder_path)
        
        for s in preset.sound_preset.sample_set.sampled_sound:
                        # temporary file                    #how it should be named 
            shutil.copy2(s.aux_TMP_WAV_FILE.name , f"{sample_folder_path}/{s.fileName}")



        #export artipreset   

        preset_folder_path=f"{target_dir}/{instrument_metadata['instrument_name']}/Common/Presets/{preset.mode}"          
        preset_file_name=f"{instrument_metadata ['instrument_name']}_{instrument_metadata ['instrument_uuid']}.artipreset"
        preset_file_path=f"{preset_folder_path}/{preset_file_name}"

        ensure_folder(preset_folder_path)
        preset.export_as_xml(preset_file_path)


        for i in mixed_sampled_sounds:
            print (f"{i.name} {i.fileName} {i.aux_key_range_top}  {i.aux_velocity_range_top}" )

        

         
        
        
  
        

 




                #mixed_sample_sound = group_list[0]   #will mix everythin into first element
                #mixed_sample_sound.fileName =  "MIX_"+ base_sample_sound.fileName
                #mixed_wav = AudioSegment.empty()


                #determine longest sample (overlay function trims everything)
                 
                
                
                
                    #print(f" {key} {s.sampleIndex}: {s.name} {s.aux_key_range} {s.aux_velocity_range} {s.aux_pan} ")

                    #wav = AudioSegment.from_wav("output/MEDSNR3T-L.wav").set_channels(2).pan(s.aux_pan)
                    

 
 
 

                    #aaa = AudioSegment.from_wav(s.aux_TMP_WAV_FILE.name)
                    #aaa.export(f"output/{s.name}.pydub.wav",format="wav")
                    #shutil.copy2(s.aux_TMP_WAV_FILE.name , f"output/{s.name}.wav")
                     
                     

        # reindex samples according to their new sequence



        # for key, group in itertools.groupby(sorted_sample_sounds, key = sort_by_key_and_velocity):
            
        #     if not str(key) in note_th_list:
        #         note_th_list.append(str(key))
        #     print(f"{key}:-----------------------------") 
        #     for s in group:
        #        # print(f"{key}:") 
        #         print(f"  {s.sampleIndex}: {s.name} {s.aux_key_range} {s.aux_velocity_range}  ")

        # print( ",".join(note_th_list))

       # for i in sample_sounds:
        #    print (i.name)

             
        #for  sp in preset.sound_preset.sample_set.sampled_sound:
        #    print (sp.aux_key_range_top)
        #grouped_by_notes = [list(g) for _, g in groupby(sorted_sample_sets, attrgetter('midi_note'))]


     #-------------   
        # sample_folder_path=f"{target_dir}/{instrument_metadata['instrument_name']}/Common/SamplePools/User/{instrument_metadata['instrument_name']}"
        # ensure_folder(sample_folder_path)

        # preset.sound_preset.sample_set.sampled_sound  = []   # remove existing records


       # for sampled_sound_data_plus_aux in parsed_instrument_samples:

         
        #    sampled_sound = OrbaPreset.SampledSound(sampled_sound_data_plus_aux)    
        #    sample_file_path=f"{sample_folder_path}/{sampled_sound.fileName}"
        #    print(f"exporting to {sample_file_path}" )
        #    sampled_sound.aux_SAMPLE.export(sample_file_path)

        #    preset.sound_preset.sample_set.sampled_sound.append(sampled_sound)
        
        #    # export new artipreset
        #    preset_folder_path=f"{target_dir}/{instrument_metadata['instrument_name']}/Common/Presets/Lead"          
        #    preset_file_name=f"{instrument_metadata ['instrument_name']}_{instrument_metadata ['instrument_uuid']}.artipreset"
        #    preset_file_path=f"{preset_folder_path}/{preset_file_name}"

        #ensure_folder(preset_folder_path)

        #preset.export_as_xml(preset_file_path)
           
          


# The BYTE byOriginalPitch contains the MIDI key number of the recorded pitch of the sample. For example, a recording of
# an instrument playing middle C (261.62 Hz) should receive a value of 60. This value is used as the default “root key” for
# the sample, so that in the example, a MIDI key-on command for note number 60 would reproduce the sound at its original
# pitch. For unpitched sounds, a conventional value of 255 should be used. Values between 128 and 254 are illegal.
# Whenever an illegal value or a value of 255 is encountered, the value 60 should be used. 

# 58 overridingRootKey This parameter represents the MIDI key number at which the sample is to be played
# back at its original sample rate. If not present, or if present with a value of -1, then
# the sample header parameter Original Key is used in its place. If it is present in the
# range 0-127, then the indicated key number will cause the sample to be played back
# at its sample header Sample Rate. For example, if the sample were a recording of a
# piano middle C (Original Key = 60) at a sample rate of 22.050 kHz, and Root Key
# were set to 69, then playing MIDI key number 69 (A above middle C) would cause a
#piano note of pitch middle C to be heard. 


for i in temp_files_to_remove:
    
    print(f"removing tmp file: {i}")
    os.unlink(i)