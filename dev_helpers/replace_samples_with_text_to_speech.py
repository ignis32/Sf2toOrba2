# this script is for debugging Orba2 artipreset, to be sure which sample is played on which note.
# after replacing samples, orba will talk the sample name.
# artipreset is modified to have a static pitch to be able to hear the voice

#expected file structure


# preset_to_dissect/Presets/
# preset_to_dissect/SamplePools/

from pydub import AudioSegment
 
from gtts import gTTS 

import sys
import os
import tempfile
# setting path
sys.path.append('.')
sys.path.append('..')
sys.path.append('./dev_helpers')


# importing  (omg that's so ugly)
import standalone.OrbaPreset.OrbaPreset   as   OrbaPreset
from standalone.OrbaPreset.OrbaPreset import PresetEntry 

#os.chdir("dev_helpers")

mode = "Lead"
artipreset="PanDrum_ea820c2d9ccd0e195b6e716bbc2e3a65.artipreset"

#language_for_voice='ru'
language_for_voice='en'

prefix_to_remove = "PanDrum"

# will generate voice "1ppA2" for this sample:
#<SampledSound sampleIndex="0" name="PanDrum1ppA2" 



def ensure_folder(path):
    # ensure folder
    try:
        os.makedirs(path)
    except FileExistsError:
    # directory already exists
        pass

def create_temp_file():
    
    tmp_file = tempfile.NamedTemporaryFile(delete=False)    # beware, it will create tmp files and not remove them. 
    tmp_file.close()
    return tmp_file
 

preset = PresetEntry()
preset.load_from_file(f"preset_to_dissect/Presets/{mode}/{artipreset}")


ensure_folder('output')

 
for s in preset.sound_preset.sample_set.sampled_sound:
    print (f"{s.name} {s.fileName}")

    # gTTS generates 22khz files. This pitch will roughly compensate for that and ensure that it will not be transposed
    s.pitch=-2


    # generate mp3 file with speech, convert to wav file, put to output.

    language = 'ru'
    print (f"getting text to speech for {s.name}")
    text = s.name.replace(prefix_to_remove,"")
    print(f"text for voice: {text}")
    tts = gTTS(text=text, lang=language_for_voice, slow=False) 
    temp_mp3 = create_temp_file()                 
    tts.save(temp_mp3.name+".mp3")
    sound = AudioSegment.from_mp3( temp_mp3.name+".mp3" )
    sound.export(f"output/{s.fileName}", format="wav")

# for i in range(len(preset.sound_preset.sample_set.sampled_sound)):
#     preset.sound_preset.sample_set.sampled_sound[i].pitch = -2

preset.export_as_xml(f"output/{artipreset}")