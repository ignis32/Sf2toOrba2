from typing import List, Optional
from enum import Enum

import  xmltodict
import sys
import logging

import re

# nice tool, btw:
#https://jsonformatter.org/xml-to-python


# helper functions

def camel_to_snake(name):
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()

 

def to_snake_case(name):
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    name = re.sub('__([A-Z])', r'_\1', name)
    name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name)
    return name.lower()




# base class that adds same functions to all other classes, each one of them representing a part of the preset XML.
class OrbaPresetElementBaseClass:

    #aux_data: dict

    def __init__(self,data=None):
        
        
        logging.debug(f"init class{self.__class__.__name__}")
        if data != None:
            #self.aux_data=data
            self.init_from_dict(data)
        
    def init_from_dict(self, aux_data):
        logging.debug(f"init_from_dict class{self.__class__.__name__}")


        #if type(aux_data) == dict:

        #muliple loops are ugly, but they allow more meaningful  linear debug output

        # yep, that's an attribute, we can just store it to the object property.
        for xml_part_name in  aux_data.keys():         
            if xml_part_name.startswith('@'):                 
                    attribute_name=xml_part_name
                    python_object_attribute_name=camel_to_snake( attribute_name.replace("@",""))

                    logging.debug(f"setting {self.__class__.__name__} attribute {xml_part_name}=\'{aux_data[attribute_name]}\'")
                    setattr(self, python_object_attribute_name ,  aux_data[attribute_name])  

        # it is just text, never seen it in orba preset, ignore it        
        for xml_part_name in  aux_data.keys():
            if xml_part_name.startswith('#'):
                    logging.warning(f"Found text part of xml, it is not expected: {xml_part_name}")
        
        # it is an element implemented as a class        
        for xml_part_name in  aux_data.keys():
            if not xml_part_name.startswith('#') and not xml_part_name.startswith('@'):
                    logging.debug( f"Attaching to {self.__class__.__name__}  child {xml_part_name}")
                    
                    element_name = xml_part_name                                # as in xml,   eg SampleSound
                    python_object_element_name = camel_to_snake(element_name)  # as in class,  eg sample_sound

                     
                    # let's see if python class with the same name as element exists 
                    if  element_name in sorted(globals()):              
                        python_class_name = element_name
                        logging.debug(f"found {python_class_name} class")
                    else:
                        # oh, yeah, name collision handling.  We expect something like Compatibility class to exist, 
                        # but actual name is  like  SynthPatchCompatibility   or ModifierChainCompatibility depending on the parent element.  
                         
                        parent_element_prefix=self.__class__.__name__.replace("class","")
                        python_class_name =  f"{parent_element_prefix}{element_name}"     
                        logging.debug(f"not found {element_name} class, assuming name collision and actual name as {python_class_name}")           
                    
                    
                    if type(aux_data[element_name]) == dict:   # just a regular element
                        
                        element = eval(f" {python_class_name} ( {aux_data[element_name]} )")    # create a new object.
                        setattr(self, python_object_element_name,  element)   #add new object to this object as a property
                                         
                    
                    elif type(aux_data[element_name]) == list:  # list, like SampleSound. Instead of one object, we need to generate a list of objects
                        element=[]
                        logging.debug(f"processing list of {python_class_name}")
                        counter=0
                        for sub_element_data in aux_data[element_name]:
                            counter+=1
                            logging.debug(f"processing item {counter} of {python_class_name}")
                            sub_element =  eval(f"{python_class_name}({sub_element_data})")   
                            element.append(sub_element)
                        setattr(self, python_object_element_name,  element)
                    
                    
                    
                 
        



#------------------------------------------------------------------------



class BezierCurvesEntry(OrbaPresetElementBaseClass):
    name: str
    bezier_curves_data: str
 


class GestureCurveAssignmentsEntry(OrbaPresetElementBaseClass):
    name: str
    curve_assignments_data: str

class EventCurveAssignmentsEntry(OrbaPresetElementBaseClass):
    name: str
    curve_assignments_data: str

class ModifierChainCompatibility(OrbaPresetElementBaseClass):
    major_version: int
    minor_version: int

class SeekerListCompatibility(OrbaPresetElementBaseClass):
    major_version: int
    minor_version: int

class ModifierChain(OrbaPresetElementBaseClass):
    compatibility: ModifierChainCompatibility
    chain_index: int
 
class PatternEntry(OrbaPresetElementBaseClass):
    name: str
    pattern_data: str
    pattern_duration: int 

class PatternList(OrbaPresetElementBaseClass):
    pattern_entry: List[PatternEntry]
 
class SeekerEntry(OrbaPresetElementBaseClass):
    input_length: str
    in_min: int
    in_max: int
    out_min: int
    out_max: int
    seeker_type: str
    event_source: Optional[str]
    note_offset: Optional[int]
    controller: Optional[str]
    trigger_source: Optional[str]
    trigger_rule: Optional[str]
    metric_sensor: Optional[str]
    metric_selection: Optional[str]
    max_rate: Optional[int]
 

class SeekerList(OrbaPresetElementBaseClass):
    seeker_entry: List[SeekerEntry]
    compatibility: ModifierChainCompatibility

class Pool(OrbaPresetElementBaseClass):
    USER = "User"


class Subdirectory(OrbaPresetElementBaseClass):
    PAN_DRUM_82301_E0_F951_DB25_C8_F25_C5548_ADD1_D45 = "PanDrum_82301e0f951db25c8f25c5548add1d45"


class SampledSound(OrbaPresetElementBaseClass):
    sample_index: int
    name: str
    loop_start: int
    loop_end: int
    pitch: str
    file_name: str
    subdirectory: Subdirectory
    pool: Pool
 
class SampleSet(OrbaPresetElementBaseClass):
    sampled_sound: List[SampledSound]
    name: str
    note_thresholds: str
    velocity_thresholds: str
    sample_map: str
 
class SynthPatchCompatibility(OrbaPresetElementBaseClass):
    audio_engine_major: int
    audio_engine_minor: int
    sample_playback: int

class SynthPatch(OrbaPresetElementBaseClass):
    compatibility: SynthPatchCompatibility
    synth_mode: int
    octave: int
    osc1_multiplier: int
    osc1_detune: int
    osc1_mix: int
    osc2_multiplier: int
    osc2_detune: int
    osc2_mix: int
    ring_mod: int
    noise_mix: int
    osc1_vibrato: int
    osc2_vibrato: int
    osc1_ramp1_start: int
    osc1_ramp1_end: int
    osc1_ramp1_time: int
    osc1_ramp2_start: int
    osc1_ramp2_end: int
    osc1_ramp2_time: int
    osc1_ramp3_start: int
    osc1_ramp3_end: int
    osc1_ramp3_time: int
    osc2_ramp1_start: int
    osc2_ramp1_end: int
    osc2_ramp1_time: int
    osc2_ramp2_start: int
    osc2_ramp2_end: int
    osc2_ramp2_time: int
    osc2_ramp3_start: int
    osc2_ramp3_end: int
    osc2_ramp3_time: int
    amp_env_attack: int
    amp_env_peak_velocity: int
    amp_env_decay: int
    amp_env_sustain: int
    amp_env_sustain_velocity: int
    amp_env_release: int
    amp_env_release_velocity: int
    filter_env_attack: int
    filter_env_peak_velocity: int
    filter_env_decay: int
    filter_env_sustain: int
    filter_env_sustain_velocity: int
    filter_env_release: int
    filter_env_release_velocity: int
    vca2_env_attack: int
    vca2_env_peak_velocity: int
    vca2_env_decay: int
    vca2_env_sustain: int
    vca2_env_sustain_velocity: int
    vca2_env_release: int
    vca2_env_release_velocity: int
    env_select: int
    wg_mode: int
    wg_pitch: int
    wg_regeneration: int
    wg_damp_on_hold: int
    wg_damp_on_release: int
    wg_mix_back: int
    wg_mix_forward: int
    wg_lfo_mod: int
    filter_mode: int
    filter_cutoff: int
    filter_cutoff_key: int
    filter_cutoff_env: int
    filter_resonance: int
    filter_resonance_env: int
    lfo_rate: int
    lfo_mode: int
    output_level: int
    reverb_level: int
    delay_level: int
    effect_select: int
    effect_depth: int
    effect_param1: int
    effect_param2: int
    mod_source1_1_destination: int
    mod_source1_1_weight: int
    mod_source1_2_destination: int
    mod_source1_2_weight: int
    mod_source1_3_destination: int
    mod_source1_3_weight: int
    mod_source2_1_destination: int
    mod_source2_1_weight: int
    mod_source2_2_destination: int
    mod_source2_2_weight: int
    mod_source2_3_destination: int
    mod_source2_3_weight: int
    mod_source3_1_destination: int
    mod_source3_1_weight: int
    mod_source3_2_destination: int
    mod_source3_2_weight: int
    mod_source3_3_destination: int
    mod_source3_3_weight: int
    mod_source4_1_destination: int
    mod_source4_1_weight: int
    mod_source4_2_destination: int
    mod_source4_2_weight: int
    mod_source4_3_destination: int
    mod_source4_3_weight: int
    mode: str
 

class SoundPreset(OrbaPresetElementBaseClass):
    synth_patch: SynthPatch
    sample_set: SampleSet
    name: str

class TuningEntry(OrbaPresetElementBaseClass):
    key: str
    name: str
    intervals: str
    midi_octave: int
    transposition_type: str
    type: str
    tuning: str
 
class CoverArt(OrbaPresetElementBaseClass):
    cover_image_ref: str
    artist: str
 
class Visuals(OrbaPresetElementBaseClass):
    
    #subclasses
    cover_art: CoverArt
    
class PresetEntry(OrbaPresetElementBaseClass):

#xml related

    # elements 
    sound_preset: SoundPreset
    modifier_chain: ModifierChain
    seeker_list: SeekerList
    bezier_curves_entry: BezierCurvesEntry
    gesture_curve_assignments_entry: GestureCurveAssignmentsEntry
    event_curve_assignments_entry: EventCurveAssignmentsEntry
    pattern_list: PatternList
    tuning_entry: TuningEntry
    visuals: Visuals

    # attributes
    name: str
    description: str
    tag_list: str 
    uuid: str
    read_only: int
    mode: str
    artist: str
    factory: int

    #auxilary
    aux_data: dict              
            
    def load_from_file(self,filename):        
        # load xml as a dict
        # 
        logging.info("loading from file")
        with open(filename) as fd:
            aux_data = xmltodict.parse(fd.read())['PresetEntry']
        self.init_from_dict(aux_data)
   
    def _init_(self):
        pass

class Welcome10:
    preset_entry: PresetEntry

    def __init__(self, preset_entry: PresetEntry) -> None:
        self.preset_entry = preset_entry




#-----------------------------------
logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("debug.log"),
            logging.StreamHandler()
        ]
        )
 
 