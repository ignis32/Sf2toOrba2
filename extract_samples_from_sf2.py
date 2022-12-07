
# # https://daizyu.com/posts/2021-09-11-001/

# # https://freepats.zenvoid.org/sf2/sfspec24.pdf

# # https://pjb.com.au/midi/sfspec21.html#6.2
 
#with open('ACCORDION.sf2', 'rb') as sf2_file:
#     sf2 = Sf2File(sf2_file)

#instrument_name = ( sf2.raw.info[b'INAM'].decode('ascii'))


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


filepath = r'ACCORDION.sf2'
#filepath = r'multi.sf2'
#filepath = r'sk.sf2'
OCTAVE_SHIFT= MIDDLE_C_IS_C3


#filepath = 'multi.sf2'
target_dir = r'output'




def number_to_note(number: int):
    NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    NOTES_IN_OCTAVE = len(NOTES)
    octave = number // NOTES_IN_OCTAVE
    note = NOTES[number % NOTES_IN_OCTAVE]
    return f"{note}{octave+OCTAVE_SHIFT}"

def gen_md5(text):
    source = text.encode()
    md5 = hashlib.md5(source).hexdigest() # returns a str
    return (md5)

def export_sample(sample, instrument_name, file_name):

    # ensure folder
    try:
        os.makedirs(f"{target_dir}/{instrument_name}")
    except FileExistsError:
    # directory already exists
        pass


    out_filepath = os.path.join(f"{target_dir}/{instrument_name}", f"{file_name}_{gen_md5(file_name)}.wav")
    sample.export(out_filepath)




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
            
            instrument_name = "SF2-"+(instrument.name).strip()  #

           # root_note = bag[Sf2Gen.OPER_OVERRIDING_ROOT_KEY].word   if Sf2Gen.OPER_OVERRIDING_ROOT_KEY in bag.gens.keys()  else (bag.sample.DEFAULT_PITCH) 
           # root note  is defined in sample, and later might be overriden in the preset zone.
            root_note = bag.base_note  if bag.base_note != None  else (bag.sample.DEFAULT_PITCH) 
   
            velocity_top = bag.velocity_range[-1] if bag.velocity_range != None else 127

            print(f"""  
              Sample: {bag.sample.name}          
              Key range:   {bag.key_range}  
              Velocity range:   {bag.velocity_range}  
            * Velocity top: {velocity_top}
              Root key midi number:  {root_note}                     
            * Root key: {number_to_note(root_note)}
            Loop status  {bag.sample_loop}
            loop start:  {bag.sample.start_loop}
            loop stop:   {bag.sample.end_loop}
            * cloop start : {bag.cooked_loop_start}
            * cloop stop :  {bag.sample.end_loop +  bag[Sf2Gen.OPER_END_LOOP_ADDR_OFFSET].short    }
            cloop stop offset:  { bag[Sf2Gen.OPER_END_LOOP_ADDR_OFFSET].short }
            
            """)
            
            #NamePart1<_namePart2_namePartn>_Note<_Velocity><_LoopStart><_LoopEnd><_UUID>.wav#
            export_sample(bag.sample, instrument_name,
             f"{instrument_name}_{number_to_note(root_note)}_{velocity_top}_{bag.cooked_loop_start}_{bag.sample.end_loop +  bag[Sf2Gen.OPER_END_LOOP_ADDR_OFFSET].short  }")

            '''

            
             43 keyRange This is the minimum and maximum MIDI key number values for which this preset zone or instrument zone is active. The LS byte indicates the highest and the MS byte the lowest valid key. The keyRange enumerator is optional, but when it does appear, it must be the first generator in the zone generator list.
             44 velRange This is the minimum and maximum MIDI velocity values for which this preset zone or instrument zone is active. The LS byte indicates the highest and the MS byte the lowest valid velocity. The velRange enumerator is optional, but when it does appear, it must be preceded only by keyRange in the zone generator list.    
               
             54 sampleModes This enumerator indicates a value which gives a variety of Boolean flags describing the sample for the current instrument zone. The sampleModes should only appear in the IGEN sub-chunk, and should not appear in the global zone. The two LS bits of the value indicate the type of loop in the sample:
              0 indicates a sound reproduced with no loop,
              1 indicates a sound which loops continuously,
              2 is unused but should be interpreted as indicating no loop, and
              3 indicates a sound which loops for the duration of key depression then proceeds to play the remainder of the sample.
           
            58 overridingRootKey This parameter represents the MIDI key number at which the sample is to be played back at its original sample rate. If not present, or if present with a value of -1, then the sample header parameter OriginalKey is used in its place. If it is present in the range 0-127, then the indicated key number will cause the sample to be played back at its sample header Sample Rate. For example, if the sample were a recording of a piano middle C (Original Key = 60) at a sample rate of 22.050 kHz, and Root Key were set to 69, then playing MIDI key number 69 (A above middle C) would cause a piano note of pitch middle C to be heard.
            '''
 
