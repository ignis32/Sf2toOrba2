
# # https://daizyu.com/posts/2021-09-11-001/

# # https://freepats.zenvoid.org/sf2/sfspec24.pdf

# # https://pjb.com.au/midi/sfspec21.html#6.2
 
import os
from sf2utils.sf2parse import Sf2File
from sf2utils.generator import Sf2Gen
import hashlib

# There is no strict assignment of the note 60 to certain octave. 
# https://petervodden.blog/portfolio/middle-c-c3-or-c4/
# note 60 can be C3 or C4 or even sometimes C5 depending on interpretation.
# goddamn standards cannot even agree on what the 60 note is. 

# Most popular
MIDDLE_C_IS_C4 = -1   
MIDDLE_C_IS_C3 = -2  


#filepath = r'Hang-D-minor-20220330.sf2'
#filepath = r'(130 sounds) 27mg_Symphony_Hall_Bank.SF2'

filepath = r'ACCORDION.sf2'
target_dir = r'output'
OCTAVE_SHIFT= MIDDLE_C_IS_C3   


def number_to_note(number: int):
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
                                    #sample_data
def export_sample(instrument_name, sd):

    
    folder_path = f"{target_dir}/{instrument_name}"

    ensure_folder(folder_path)

    uuid=md5sum(f"{instrument_name}_{sd['root_note_text']}_{sd['velocity_range_top']}")

    #NamePart1<_namePart2_namePartn>_Note<_Velocity><_LoopStart><_LoopEnd><_UUID>.wav    Subskybox's naming convetion.
    filename = f"SF2-{instrument_name}_{sd['root_note_text']}_{sd['velocity_range_top']}_{sd['loop_start_offset']}_{sd['loop_end_offset']}_{uuid}.wav"

    out_filepath = os.path.join(folder_path, filename)
    sd['sample'].export(out_filepath)




with open(filepath, 'rb') as sf2_file:
    
    #use sf2util library to parse sf2 bank
    sf2 = Sf2File(sf2_file)

    print ("\n\n\n")
    print (f"number of instruments in the sf2: {len(sf2.instruments)-1}")   #/// there is an additional EOI fake instrument in the end, marks end of instrument list
    

    # instrument - In the SoundFont standard, a collection of zones which represents the sound of a single musical instrument or sound effect set.
    # one sf2 file might contain multiple instruments.

    for instrument in sf2.instruments:
        
        if  instrument.name  == "EOI":  # this is not a real instrument, "EOI" indicating end of instruments.
            continue       
        
        print (f"Instrument: { instrument.name} #{instrument.bag_size}     {instrument.bag_idx}")
        # print (instrument.pretty_print())
        
        # bag - A SoundFont data structure element containing a list of preset zones or instrument zones
        # instrument zone - A subset of an instrument containing a sample reference and associated articulation data defined to play over certain key numbers and velocities.
        # preset zone - A subset of a preset containing an instrument reference and associated articulation data defined to play over certain key numbers and velocities.
      
        for bag in instrument.bags:
            if  (bag.sample) == None:
 
                print("no sample bag")  # I am not sure why these appear in bags, but whatever. most probably is has something to do with global zones.
                continue
            #print (bag.pretty_print())
            
            instrument_name = (instrument.name).strip()  
     

            sample_data = {
                'sample_name':        bag.sample.name,        
                'sample':             bag.sample,            #object, that can be exported as wav later.
                'key_range':          bag.key_range, 
                'key_range_top':      bag.key_range[-1] if bag.key_range != None else 127 ,   #  was planned to use with Orba note threshold, but seems like orba does not allow to set range.
                'velocity_range':     bag.velocity_range,  
                'velocity_range_top': bag.velocity_range[-1] if bag.velocity_range != None else 127,  # used for Orba2 velocity threshold
                'root_note':                         bag.base_note if bag.base_note != None  else (bag.sample.DEFAULT_PITCH) ,  # used to assign sample to note. base_note (root note override) might be absent, in this case default sample's pitch kicks in.
                'root_note_text':     number_to_note(bag.base_note if bag.base_note != None  else (bag.sample.DEFAULT_PITCH)),  # used to name a sample file 
                'loop_start_offset':  bag.cooked_loop_start , # when note is played for long, it goes to the loop. This loop is a part of initial sample.
                'loop_end_offset':    bag.sample.end_loop +  bag[Sf2Gen.OPER_END_LOOP_ADDR_OFFSET].short,  # seems like end loop offset is counted from the loop start using negative values.
                'sample-rate': bag.sample.sample_rate,  # required for the future sample rate  pitch compensation
                'pitch_correction_coefficient':  48000/bag.sample.sample_rate
            }
 
            print (sample_data)
            export_sample(instrument_name, sample_data)

            
           

            
            #  43 keyRange This is the minimum and maximum MIDI key number values for which this preset zone or instrument zone is active. The LS byte indicates the highest and the MS byte the lowest valid key. The keyRange enumerator is optional, but when it does appear, it must be the first generator in the zone generator list.
            #  44 velRange This is the minimum and maximum MIDI velocity values for which this preset zone or instrument zone is active. The LS byte indicates the highest and the MS byte the lowest valid velocity. The velRange enumerator is optional, but when it does appear, it must be preceded only by keyRange in the zone generator list.    
               
            #  54 sampleModes This enumerator indicates a value which gives a variety of Boolean flags describing the sample for the current instrument zone. The sampleModes should only appear in the IGEN sub-chunk, and should not appear in the global zone. The two LS bits of the value indicate the type of loop in the sample:
            #   0 indicates a sound reproduced with no loop,
            #   1 indicates a sound which loops continuously,
            #   2 is unused but should be interpreted as indicating no loop, and
            #   3 indicates a sound which loops for the duration of key depression then proceeds to play the remainder of the sample.
           
            #  58 overridingRootKey This parameter represents the MIDI key number at which the sample is to be played back at its original sample rate. If not present, or if present with a value of -1, then the sample header parameter OriginalKey is used in its place. If it is present in the range 0-127, then the indicated key number will cause the sample to be played back at its sample header Sample Rate. For example, if the sample were a recording of a piano middle C (Original Key = 60) at a sample rate of 22.050 kHz, and Root Key were set to 69, then playing MIDI key number 69 (A above middle C) would cause a piano note of pitch middle C to be heard.
       
     