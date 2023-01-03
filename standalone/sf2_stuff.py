from sf2utils.sf2parse import Sf2Instrument
from sf2utils.sf2parse import Sf2File
from sf2utils.generator import Sf2Gen
from sf2utils.bag import Sf2Bag
from sf2utils.sample import Sf2Sample
import copy
from typing import List, Dict

import config_convertor
import helpers
import itertools
# classes to represent sf2 instrument in more convenient abstraction level, more suitable  for orba usecase than raw sf2utils. 
# I hope so.

class SF2O2_Sample:
    
    slug_name: str
    original_name: str   # used as ID to identify samples
    
    mixed: bool
    mixed = False

    used_by_bag: bool
    used_by_bag = False
    ##sampled_sound_generation
    #direct
    loop_start: int
    loop_end: int
    sample_index: int
    pitch: float
    #indirect
    coarse_tuning_semitones: int
    fine_tuning_cents: int 
    root_note: int
    

    def __init__(self, bag: Sf2Bag):
        sample: Sf2Sample = bag.sample

        self.slug_name  = helpers.slugify_name(sample.name)
        self.original_name  =  sample.name
        self.sample_rate = sample.sample_rate

        #  export sample to temporary file, and remember where.
        self.tmp_wav_file = helpers.generate_temp_filepath(self.slug_name)
        sample.export(self.tmp_wav_file)

        ## stuff for future samplesound generation   
        # # problem is, that SF2 allows for  params being set for each bag independently, while multiple bags can  point to single sample
        # # in orba we have only one set of settings per sample. We will just take the first one we met. Have no idea how to do that better.

        #direct
        self.sample_index = 0  #   we cannot determine index at this point yet. Will sort and set indexes later. 
        self.loop_start =  bag.cooked_loop_start if bag.sample_loop !=None and bag.sample_loop !=False else 0 # if there is no loop, in orba it means 0 for both start and end
        self.loop_end   =  bag.cooked_loop_end   if bag.sample_loop !=None and bag.sample_loop !=False else 0
 
       
        #indirect
        self.coarse_tuning_semitones  = bag.tuning  if bag.tuning != None else 0
        self.fine_tuning_cents   =  bag.fine_tuning if bag.fine_tuning != None else 0
        self.root_note =  bag.base_note if bag.base_note != None  else (bag.sample.original_pitch)    
        self.midi_key_pitch_influence = bag.midi_key_pitch_influence
       
        print(f"calculating pitch for sample {self.slug_name}")
        self.pitch = helpers.note_to_pitch(self.root_note, coarse_tuning_semitones = self.coarse_tuning_semitones, fine_tuning_cents=self.fine_tuning_cents, sample_rate = self.sample_rate, midi_key_pitch_influence = bag.midi_key_pitch_influence)  
    
    def generate_sampled_sound_dict(self, instrument_slug_name, mode):

        sample_uuid = helpers.md5sum ( f"{instrument_slug_name}_{self.slug_name}_{self.root_note}" )

        filename =    f"SF2_{instrument_slug_name}_{self.slug_name}_{self.root_note}_{sample_uuid}.wav"      
        #filename =    f"{instrument_slug_name}_{self.slug_name}_{note_to_text(root_note)}_{sample_uuid}.wav"            

        return   {
                    '@sampleIndex':   self.sample_index,
                    '@name':          self.slug_name,
                    '@loopStart':     self.loop_start, # if there is no loop, in orba it means 0 for both start and end
                    '@loopEnd':       self.loop_end,
                    '@pitch':         self.pitch ,
                    '@fileName':      filename,
                    '@subdirectory':  f"SF2_{instrument_slug_name}_{mode}",
                    '@pool': "User"
                }

    
class SF2O2_Bag:
    
    slug_name: str
    original_name: str
    splited = False  #indicates if this sf2o2 bag is a result of splitting key range to individual notes.
    sample_original_name: str  # used to look up for sf2o2 in the instrument unique sf2o2 samples list SF2O2_Instrument->sf2o2_samples
    key_range_top: int
    velocity_range_top: int

    #key_vel: str  # combination of top key and velocity used to determine overlapping. dynamically generated property now.
    @property
    def key_vel(self):
        return f"{self.key_range_top}_{self.velocity_range_top}"   #self._key_vel

 
    def __init__(self, bag: Sf2Bag):

        self.original_name = bag.sample.name # kind of stupding thing, bag does not have a name. Polyphone uses sample name, but it is not unique, one sample can be used for different bags.
        self.sample_original_name = bag.sample.name 
     
        if bag.key_range == None:  #this happens for strange cases when one sample is for all
            bag.key_range == [0,127]

            #raise ValueError("WTF")
        
        self.key_range_bottom  = bag.key_range[0] if bag.key_range != None else 0
        self.key_range_top  = bag.key_range[-1] if bag.key_range != None else 127
       
        self.velocity_range_top = bag.velocity_range[-1] if bag.velocity_range != None and bag.velocity_range != False else 127
       # self.key_vel = f"{self.key_range_top}_{self.velocity_range_top}"
      
        self.slug_name = helpers.slugify_name("BAG_"+bag.sample.name  + "_"+ self.key_vel) #  trying to invent some meaningful and more or less unique name.

class SF2O2_Instrument:
  
    slug_name: str                          # slugfied name for filesystem.
    original_name: str
    sf2o2_bags:    List [SF2O2_Bag]         # parsed bags with corresponding sample names
    sf2o2_samples: List [SF2O2_Sample]      # list of unique samples
    default_bag: SF2O2_Bag
    
    original_instrument: Sf2Instrument  # it is actually used, stop removing it each time, idiot.
  
    def exists_sample_name(self, original_name: str)  -> bool :
        return  ( _:=[x for x in self.sf2o2_samples if x.original_name ==   original_name    ] )
    
    def find_sample_by_name (self, original_name ):    
        found_samples = [x for x in self.sf2o2_samples if x.original_name ==   original_name ] 
        
        if len(found_samples) > 1:
            raise ValueError("How I've ended up with multiple samples with the same name") 

       # print( [x for x in self.sf2o2_samples if x.original_name ==  original_name ][0].sample_index )
        return   [x for x in self.sf2o2_samples if x.original_name ==  original_name ][0] 

    # determine if there is already a bag with the same key range top and velocity ( it means that we have two samples playing in the same time in sf2, and orba cannot do it)
    def exists_key_velocity_overlap(self, sf2o2_bag: SF2O2_Bag ) -> bool :
        return  ( _:=[x for x in self.sf2o2_bags if x.key_vel ==  sf2o2_bag.key_vel] )  #

    def find_overlapping_bag_to_mix(self, sf2o2_bag: SF2O2_Bag ):    # return actual element for mixing
        overlapping_bags = [x for x in self.sf2o2_bags if x.key_vel ==  sf2o2_bag.key_vel] 
        if len(overlapping_bags) > 1:
            raise ValueError("How I've ended up with multiple overlapping bags") 
        return   [x for x in self.sf2o2_bags if x.key_vel ==  sf2o2_bag.key_vel][0] 


    #  adds bag or initializes mixing(tba)     
    def add_sf2o2_bag(self,sf2o2_bag: SF2O2_Bag ): 
            if ( self.exists_key_velocity_overlap(sf2o2_bag) ):
                #TBA here will be mixing. At this moment, just reject the bag and skip it.
                print(f"discarded bag {sf2o2_bag.__dict__} due to key range overlapping, TBA mixing")
                print(f"mixing should happen with bag {self.find_overlapping_bag_to_mix(sf2o2_bag).__dict__}")
            else :
                self.sf2o2_bags.append(sf2o2_bag) 
 
    def split_bag_range_to_single_notes(self, sf2o2_bag: SF2O2_Bag):

        if sf2o2_bag.key_range_bottom == sf2o2_bag.key_range_top:  # actually, it is one note range bag already nothing to do.
            #print(f"not splitting one-note range bag {sf2o2_bag.slug_name}")
            return [sf2o2_bag]

        splitted_sf2o2_bags=[]
        print(f"splitting {sf2o2_bag.slug_name}")
                                                   #cursed python ranges..
        for i in range(sf2o2_bag.key_range_bottom, sf2o2_bag.key_range_top+1):
            print(f"split: {i}")
            new_sf2o2_bag: SF2O2_Bag  = copy.deepcopy(sf2o2_bag)
            new_sf2o2_bag.key_range_top = i
           # new_sf2o2_bag.key_vel = f"{new_sf2o2_bag.key_range_top}_{new_sf2o2_bag.velocity_range}"  # is dynamically generated now
            new_sf2o2_bag.slug_name=f"{new_sf2o2_bag.slug_name}_split{i}"
            new_sf2o2_bag.splited=True
            splitted_sf2o2_bags.append(new_sf2o2_bag)
        return splitted_sf2o2_bags
            
    # adds a sample into instrument sample list only if there no sample with the same name.
    # i do not wont wearing SSD by exporting same sample multiple times.
    def add_only_unique_sample_from_bag(self, bag: Sf2Bag):  # have to pass bag, not sample, as bag has same sample properties.

         sample=bag.sample
                                    # refered as sample_original_name in sf2o2 bag
         if self.exists_sample_name(sample.name) :  # looks like this sample had been already added for some other bag. 
            print (f"skipping adding  {sample.name}  sample as duplicate")
         else:
            print (f" adding unique {sample.name}  sample ")
            sf2o2_sample = SF2O2_Sample(bag) # creates an object and corresponding temporary file with wav.
            self.sf2o2_samples.append(sf2o2_sample)    

    def remove_unused_samples(self):
            print("==========================")
            print("removing unused samples \n\n")

            # mark all samples that are used by bags
            for sb in self.sf2o2_bags:
                for ss in self.sf2o2_samples:
                    if sb.sample_original_name == ss.original_name:
                        ss.used_by_bag=True
            # print unused samplesd
            for ss in self.sf2o2_samples:
                if not ss.used_by_bag:
                    print(f"clearing unused sample: {ss.original_name}")

            # regenerate list of samples
            self.sf2o2_samples = [obj for obj in self.sf2o2_samples if obj.used_by_bag]

    def reindex_samples(self):
        
        for idx,s in  enumerate(self.sf2o2_samples):
            s.sample_index = idx

    def load_samples_and_bags(self, mode="Lead"):

       
        for bag in self.original_instrument.bags:      

            if  (bag.sample) == None:
                self.default_original_bag = bag  # this bag seems to store some default settings for pan, adsr, bla bla bla. #TBA - use it.
                continue
             
            sf2o2_bag = SF2O2_Bag(bag)  #candidate, it can be declined/mixed if same key and velocity already exists.          
            self.add_only_unique_sample_from_bag(bag)  
           
            if mode == 'Drums': # in case of Drum instruments, Orba2 does not allow using sample for the note range. 
                                # therefore, let's split it to multiple sf2o2_bags, each one with one note.
                for per_note_splitted_sf2o2_bag in self.split_bag_range_to_single_notes(sf2o2_bag):
                    self.add_sf2o2_bag(per_note_splitted_sf2o2_bag)
            else:
                self.add_sf2o2_bag(sf2o2_bag)      
        
        if mode == "Drums":
            filtered_sf2o2_bags=[]
            for b in self.sf2o2_bags:
                if int(b.key_range_top) in  [36,38,42,46,45,50,70,49,39]:
                    filtered_sf2o2_bags.append(b)
            self.sf2o2_bags =  filtered_sf2o2_bags



        self.remove_unused_samples()
        self.reindex_samples()  #

    def sort_sf2o2_bags(self):

       #  by_key      = lambda x:   int(x.aux_key_range_top)   
       #  by_velocity = lambda x:   int(x.aux_velocity_range_top)   
        by_key_and_velocity     = lambda x:   ( int(x.key_range_top), int(x.velocity_range_top)   )
        sorted_sf2o2_bags = sorted(self.sf2o2_bags, key=by_key_and_velocity)
        self.sf2o2_bags = sorted_sf2o2_bags 

    def get_grouped_bags_by_key(self):
        by_key     = lambda x:   ( int(x.key_range_top)  )
        return itertools.groupby( self.sf2o2_bags , key = by_key)

   
    def generate_sample_groups(self):
        self.sort_sf2o2_bags()

        note_thresholds_list   = []
        sample_mappings_list   = []
        velocity_thresholds_list = []

        key_grouped_bags = self.get_grouped_bags_by_key()  # velocity is anyway expected to be different for each next bag, as otherwise bag will be discarded before
        
        for key, group in  key_grouped_bags:          
          #  print(f"---group--- {key} ")    
            group_velocity_threshold = []
            group_sample_mapping = []
            note_thresholds_list.append(str(key))
                  
            for b in group:
              #      print(f"searching sample {b.sample_original_name} result {self.find_sample_by_name(b.sample_original_name).sample_index}" )
                    group_sample_mapping.append(self.find_sample_by_name(b.sample_original_name).sample_index)                
                    group_velocity_threshold.append(b.velocity_range_top)
                
                
            group_velocity_threshold.pop() # two samples for two rangers mean only one value in orba, last one is ommited. 
            sample_mappings_list.append(group_sample_mapping)
            velocity_thresholds_list.append(group_velocity_threshold)
        #note_thresholds_list.pop() # note threshold always has one less element than mappings. (last one is ommited)
        

        self.note_thresholds_list = note_thresholds_list
        self.sample_mappings_list =  sample_mappings_list
        self.velocity_thresholds_list = velocity_thresholds_list

        print (f"noteth: {note_thresholds_list}")
        print (f"vel_th: {velocity_thresholds_list}")
        print (f"vel_th:  {sample_mappings_list}")

    #converting to  strings that will be used in xml
    # convert to single string
    @property
    def note_thresholds(self) -> str: 
        note_thresholds_list_no_last_element= copy.deepcopy(self.note_thresholds_list)
        note_thresholds_list_no_last_element.pop()
        note_thresholds     = ",".join(note_thresholds_list_no_last_element)
        return note_thresholds     
    
    @property
    def sample_mappings(self) -> str: 
        sample_mappings     = str(self.sample_mappings_list)[1:-1].replace(" ", "").replace( ("],["), "][")
        return sample_mappings

    @property
    def velocity_thresholds(self) -> str: 
        velocity_thresholds     = str(self.velocity_thresholds_list)[1:-1].replace(" ", "").replace( ("],["), "][")
        return velocity_thresholds
    

        #return note_thresholds, sample_mappings, velocity_thresholds

    def __init__(self, instrument:Sf2Instrument, mode="Lead"):
        
        self.slug_name = helpers.slugify_name(instrument.name)
        self.original_name = instrument.name
        
        print (f"LOADING INSTRUMENT {self.original_name}")

        self.original_instrument = instrument

        self.sf2o2_samples=[]
        self.sf2o2_bags=[]
        self.load_samples_and_bags(mode=mode)
        self.generate_sample_groups()   ## TBA how about note threshold  generation using @property decorators? 


##--------------------------------- standalone functions


def load_sf2_file():
    
    sf2_filepath = f"{config_convertor.sf2_folder_path}/{config_convertor.sf2_filename}"
    sf2_file = open(sf2_filepath, "rb")  # We need this file to be opened until the end of the script, or sample exporting will not work (after closing the handler)
    #with open(sf2_filepath, 'rb') as sf2_file:    
    sf2 = Sf2File(sf2_file)
    print (f"loading sf2 {sf2_file}, number of instruments in the sf2: {len(sf2.instruments)-1}")   #/// there is an additional EOI fake instrument in the end, marks end of instrument list
    return sf2

        
def load_sf2o2_instruments(mode="Lead")   ->   List [SF2O2_Instrument] :
       
        sf2 = load_sf2_file()
        filtered_sf2o2_instruments = []
        for instrument in sf2.instruments:
            if instrument.name == 'EOI': # not a real instrument, just End Of Instruments marker.
                continue

            #TBA regex instead maybe?
            if config_convertor.search_for_instrument in instrument.name:  # search for specific name of the instrument. "" will choose them all.
                sf2o2_instrument = SF2O2_Instrument(instrument,mode=mode)
                filtered_sf2o2_instruments.append(sf2o2_instrument)
                print (f"Added instrument {sf2o2_instrument.original_name}  as  {sf2o2_instrument.slug_name}")
        return filtered_sf2o2_instruments 

def clean_tmp():
 
    helpers.remove_temp_files()