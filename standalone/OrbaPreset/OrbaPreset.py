from typing import List, Optional
import xmltodict
import sys
import logging
import re  # for camel_case conversion

#---
# nice tool, btw, initial classes had been generated with
# https://jsonformatter.org/xml-to-python
# another similar but did not use it
# https://codebeautify.org/xml-to-python-pojo-generator


# helper functions

# convert xml element names to object property names
def camel_to_snake(name):
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()

# def to_snake_case(name):
#     name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
#     name = re.sub('__([A-Z])', r'_\1', name)
#     name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name)
#     return name.lower()

# convert object property names  back to xml element names
def to_pascal_case(snake_str):
    components = snake_str.split('_')
    # We capitalize the first letter of each component except the first one
    # with the 'title' method and join them together.
    return components[0].title() + ''.join(x.title() for x in components[1:])


# base class that adds same functions to all other classes, each one of them representing a part of the preset XML.
class OrbaPresetElementBaseClass:

    #aux_data: dict

    def __init__(self, data=None):
        logging.debug(f"init  {self.__class__.__name__}")

        # #PresetEntry does not have incoming json data yet
        # if   self.__class__.__name__  != "PresetEntry":
        # #if data != None:   # works too, but intention is not so clear
        self.init_from_dict(data)

    # object loads data from the dict structure, and recusively does the same for each class-implemented property,
    # passing relevant part of the dict further to next objects.

    def init_from_dict(self, aux_data):
        logging.debug(f"init_from_dict class {self.__class__.__name__}")

        # muliple loops are ugly, but they allow more meaningful linear debug output

        # yep, that's an attribute, we can just store it to the object property.
        for xml_part_name in aux_data.keys():
            if xml_part_name.startswith('@'):
                attribute_name = xml_part_name
                python_object_attribute_name = ( attribute_name.replace("@", ""))  # no snake anymore

                logging.debug( f"setting {self.__class__.__name__} attribute {xml_part_name}=\'{aux_data[attribute_name]}\'")

                # properties defined in class definition are note strict, more like used for autocomplete
                setattr(self, python_object_attribute_name, aux_data[attribute_name])    

        # it is just text, never seen it in orba2 preset, ignore it
        for xml_part_name in aux_data.keys():
            if xml_part_name.startswith('#'):
                logging.warning( f"Found text part of xml, it is not expected: {xml_part_name}")

        # it is an element implemented as a class
        for xml_part_name in aux_data.keys():
            if not xml_part_name.startswith('#') and not xml_part_name.startswith('@'):
                logging.debug(  f"Attaching to {self.__class__.__name__}  child {xml_part_name}")
         
                element_name = xml_part_name                               # as in xml,   eg SampleSound
                python_object_element_name = camel_to_snake(element_name)  # as in class,  eg sample_sound

                # let's see if python class with the same name as element exists
                if element_name in sorted(globals()):
                    python_class_name = element_name
                    logging.debug(f"found {python_class_name} class")
                else:
                    # oh, yeah, name collision handling.  We expect something like Compatibility class to exist as it is in XML,
                    # but actual class name is  like  SynthPatchCompatibility   or ModifierChainCompatibility depending on the parent element class name.
                    # as soon as there are tons of different Compatibility elements
 
                    parent_element_prefix = self.__class__.__name__
                    python_class_name = f"{parent_element_prefix}{element_name}"
                    logging.debug(  f"not found {element_name} class, assuming name collision and actual name as {python_class_name}")

                if type(aux_data[element_name]) == dict:   # just a regular element

                    # create a new object.
                    # we are searching python class name and create instance of it, initializing 
                    # with it's section of the data dict.

                    element = eval( f" {python_class_name} ( {aux_data[element_name]} )")  
                    # add new object to this object as a property
                    setattr(self, python_object_element_name,  element)

                # list, like SampleSound. Instead of one object, we need to generate a list of objects

                elif type(aux_data[element_name]) == list:
                    element = []
                    logging.debug(f"processing list of {python_class_name}")
                    counter = 0

                    # initialize each object in the list
                    for sub_element_data in aux_data[element_name]:
                        counter += 1
                        logging.debug(  f"processing item {counter} of {python_class_name}")
                        sub_element = eval( f"{python_class_name}({sub_element_data})")
                        element.append(sub_element)
                    setattr(self, python_object_element_name,  element)

    # generate dict from the object, that is suitable for xmltodict.unparse xml generation   https://github.com/martinblech/xmltodict
    # '@...': means attributes

    def get_as_dict(self):
        logging.debug(f"get_as_dict class {self.__class__.__name__}")
        data = self.__dict__.copy()  # we cannot modify original dict keys on the fly, so we modify the copy.
        
        # use current object properties provided by __dict__ 
        for i in self.__dict__.keys():

            # trying to distingush elements, elements list and attributes 

            # attribute.
            if type(data[i]) == str or type(data[i]) == int:
                # seems like xmltodict has some issue with this symbol )en dash)
                attribute_value = data.pop(i).replace(r"–", "-")
                # just rename according to xmltodict convention, by removing old element and adding new
                data[f"@{(i)}"] = attribute_value

            # list of elements
            elif type(data[i]) == list:

                data.pop(i)     # remove old name
                data_list = []
                # iterating list of elements
                for sub_element in self.__dict__[i]:  #again, we are iterating original data here, as list from data[i] jsut had bee removed.
                    data_list.append(sub_element.get_as_dict())  # recursion here, underlying objects should provide their dicts too.

                data[f"{to_pascal_case(i)}"] = data_list  # also, converting back from snake_case to original element's PascalCase name.

            # element
            elif isinstance(data[i], OrbaPresetElementBaseClass):
                data.pop(i)
                data[f"{to_pascal_case(i)}"] = getattr( self,  i).get_as_dict()    # same as above but just for one standalone element
        
            else:
                raise(
                    f"Do not know what to do with {data[i]}  {type(data[i])}")

        return data

    # convert dict prepared for xmltodict  to xml.
    def get_as_xml(self):
        return xmltodict.unparse(
            {
                self.__class__.__name__: self.get_as_dict()       
            
            }, pretty=True, encoding='utf-8')

    def export_as_xml(self, filename):
        with open(filename, "w") as file1:
            file1.write(self.get_as_xml())


# ------------------------------------------------------------------------


class BezierCurvesEntry(OrbaPresetElementBaseClass):
    name: str
    bezierCurvesData: str


class GestureCurveAssignmentsEntry(OrbaPresetElementBaseClass):
    name: str
    curveAssignmentsData: str


class EventCurveAssignmentsEntry(OrbaPresetElementBaseClass):
    name: str
    curveAssignmentsData: str


class ModifierChainCompatibility(OrbaPresetElementBaseClass):
    majorVersion: int
    minorVersion: int


class SeekerListCompatibility(OrbaPresetElementBaseClass):
    majorVersion: int
    majorVersion: int


class ChordModifierParams(OrbaPresetElementBaseClass):
    majorChordList: str
    minorChordList: str


class ModifierEntry(OrbaPresetElementBaseClass):
    chord_modifier_params: ChordModifierParams
    chainIndex: int
    prioIndex: int
    modifierUuid: str
    modifierType: str
    eventsInSource: str
    eventsInLength: str
    eventsOutCurve: int


class ModifierChain(OrbaPresetElementBaseClass):
    compatibility: ModifierChainCompatibility
    modifier_entry: ModifierEntry  # appeared in chords
    chainIndex: int


class PatternEntry(OrbaPresetElementBaseClass):
    name: str
    patternData: str
    patternDuration: int


class PatternList(OrbaPresetElementBaseClass):
    pattern_entry: List[PatternEntry]


class SeekerEntry(OrbaPresetElementBaseClass):
    inputLength: str
    inMin: int
    inMax: int
    outMin: int
    outMax: int
    seekerType: str
    eventSource: Optional[str]
    noteOffset: Optional[int]
    controller: Optional[str]
    triggerSource: Optional[str]
    triggerRule: Optional[str]
    metricSensor: Optional[str]
    metricSelection: Optional[str]
    maxRate: Optional[int]


class SeekerList(OrbaPresetElementBaseClass):
    seeker_entry: List[SeekerEntry]
    compatibility: ModifierChainCompatibility


class CymbalPatch(OrbaPresetElementBaseClass):  # only  drum stuff
    cymbalMode: int
    ampVelocity: int
    pitch: int
    color: int
    filterCutoff: int
    filterVelocity: int
    filterDecay: int
    decayRelease: int
    decayHold: int
    flamCount: int
    flamRate: int
    level: int
    pan: int
    fx: int
    index: int


class DrumPatch(OrbaPresetElementBaseClass):  # only  drum stuff
    drumMode: int
    ampVelocity: int
    snapLevel: int
    snapColor: int
    bendDepth: int
    bendTime: int
    modulationRatio: int
    modulationDetune: int
    modulationDepth: int
    modulationVelocityDepth: int
    decayRelease: int
    decayHold: int
    ensnare: int
    grit: int
    flamCount: int
    flamRate: int
    fuzz: int
    level: int
    pan: int
    tailLevel: int
    tailDelay: int
    tailDecay: int
    fx: int
    note: int
    index: int


class ShakerPatch(OrbaPresetElementBaseClass):  # only  drum stuff
    shakerMode: int
    velocityResponse: int
    shakeResponse: int
    pitch: int
    resonance: int
    density: int
    decay: int
    level: int
    pan: int
    fx: int


class SampleDrumPatch(OrbaPresetElementBaseClass):  # only drum stuff
    index: int
    drumMode: int
    ampVelocity: int
    snapVelocity: int
    snapLevel: int
    snapColor: int
    bendVelocity: int
    bendDepth: int
    bendTime: int
    gainRampStart: int
    gainRampEnd: int
    gainRampTime: int
    clipRampStart: int
    clipRampEnd: int
    clipRampTime: int
    fwRampStart: int
    fwRampEnd: int
    fwRampTime: int
    decayRelease: int
    decayHold: int
    flamCount: int
    flamRate: int
    level: int
    pan: int
    tailLevel: int
    tailDelay: int
    tailDecay: int
    fx: int
    note: int
    midiNote: int
    priority: int


class KitPatchCompatibility(OrbaPresetElementBaseClass):  # only drum stuff
    audioEngineMajor: int
    audioEngineMinor: int
    samplePlayback: int
    numDrums: int
    numCymbals: int
    numShakers: int
    numSampleDrums: int


class KitPatch(OrbaPresetElementBaseClass):  # only  drum stuff
    drum_patch: List[DrumPatch]
    cymbal_patch: List[CymbalPatch]
    shaker_patch: ShakerPatch


class Pool(OrbaPresetElementBaseClass):
    USER = "User"


class Subdirectory(OrbaPresetElementBaseClass):
    PAN_DRUM_82301_E0_F951_DB25_C8_F25_C5548_ADD1_D45 = "PanDrum_82301e0f951db25c8f25c5548add1d45"


class SampledSound(OrbaPresetElementBaseClass):
    sampleIndex: int
    name: str
    loopStart: int
    loopEnd: int
    pitch: str
    fileName: str
    subdirectory: Subdirectory
    pool: Pool


class SampleSet(OrbaPresetElementBaseClass):
    sampled_sound: List[SampledSound]
    name: str
    noteThresholds: str
    velocityThresholds: str
    sampleMap: str


class SynthPatchCompatibility(OrbaPresetElementBaseClass):
    audioEngineMajor: int
    audioEngineMinor: int
    samplePlayback: int


class SynthPatch(OrbaPresetElementBaseClass):
    synthMode: int
    octave: int
    osc1Multiplier: int
    osc1Detune: int
    osc1Mix: int
    osc2Multiplier: int
    osc2Detune: int
    osc2Mix: int
    ringMod: int
    noiseMix: int
    osc1Vibrato: int
    osc2Vibrato: int
    osc1Ramp1Start: int
    osc1Ramp1End: int
    osc1Ramp1Time: int
    osc1Ramp2Start: int
    osc1Ramp2End: int
    osc1Ramp2Time: int
    osc1Ramp3Start: int
    osc1Ramp3End: int
    osc1Ramp3Time: int
    osc2Ramp1Start: int
    osc2Ramp1End: int
    osc2Ramp1Time: int
    osc2Ramp2Start: int
    osc2Ramp2End: int
    osc2Ramp2Time: int
    osc2Ramp3Start: int
    osc2Ramp3End: int
    osc2Ramp3Time: int
    ampEnvAttack: int
    ampEnvPeakVelocity: int
    ampEnvDecay: int
    ampEnvSustain: int
    ampEnvSustainVelocity: int
    ampEnvRelease: int
    ampEnvReleaseVelocity: int
    filterEnvAttack: int
    filterEnvPeakVelocity: int
    filterEnvDecay: int
    filterEnvSustain: int
    filterEnvSustainVelocity: int
    filterEnvRelease: int
    filterEnvReleaseVelocity: int
    vca2EnvAttack: int
    vca2EnvPeakVelocity: int
    vca2EnvDecay: int
    vca2EnvSustain: int
    vca2EnvSustainVelocity: int
    vca2EnvRelease: int
    vca2EnvReleaseVelocity: int
    envSelect: int
    wgMode: int
    wgPitch: int
    wgRegeneration: int
    wgDampOnHold: int
    wgDampOnRelease: int
    wgMixBack: int
    wgMixForward: int
    wgLFOMod: int
    filterMode: int
    filterCutoff: int
    filterCutoffKey: int
    filterCutoffEnv: int
    filterResonance: int
    filterResonanceEnv: int
    lfoRate: int
    lfoMode: int
    outputLevel: int
    reverbLevel: int
    delayLevel: int
    effectSelect: int
    effectDepth: int
    effectParam1: int
    effectParam2: int
    modSource1_1Destination: int
    modSource1_1Weight: int
    modSource1_2Destination: int
    modSource1_2Weight: int
    modSource1_3Destination: int
    modSource1_3Weight: int
    modSource2_1Destination: int
    modSource2_1Weight: int
    modSource2_2Destination: int
    modSource2_2Weight: int
    modSource2_3Destination: int
    modSource2_3Weight: int
    modSource3_1Destination: int
    modSource3_1Weight: int
    modSource3_2Destination: int
    modSource3_2Weight: int
    modSource3_3Destination: int
    modSource3_3Weight: int
    modSource4_1Destination: int
    modSource4_1Weight: int
    modSource4_2Destination: int
    modSource4_2Weight: int
    modSource4_3Destination: int
    modSource4_3Weight: int
    mode: str


class SoundPreset(OrbaPresetElementBaseClass):
    synth_patch: SynthPatch
    sample_set: SampleSet
    name: str


class TuningEntry(OrbaPresetElementBaseClass):
    key: str
    name: str
    intervals: str
    midiOctave: int
    transpositionType: str
    type: str
    tuning: str


class CoverArt(OrbaPresetElementBaseClass):
    coverImageRef: str
    artist: str


class Visuals(OrbaPresetElementBaseClass):

    # subclasses
    cover_art: CoverArt


class PresetEntry(OrbaPresetElementBaseClass):

    # xml related

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
    tagList: str
    uuid: str
    readOnly: int
    mode: str
    artist: str
    factory: int

    # auxilary
    aux_data: dict

    def load_from_file(self, filename):
        # load xml as a dict
        #
        logging.info("loading from file")
        with open(filename) as fd:
            aux_data = xmltodict.parse(
                fd.read(), encoding='utf-8')['PresetEntry']
        self.init_from_dict(aux_data)

    def __init__(self, data=None):
        logging.debug(f"init  {self.__class__.__name__}")

    #     self.init_from_dict(data)


class Welcome10:
    preset_entry: PresetEntry

    def __init__(self, preset_entry: PresetEntry) -> None:
        self.preset_entry = preset_entry


# -----------------------------------
logging.basicConfig(
    level=logging.WARN,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)
