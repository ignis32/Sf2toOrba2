# this script is for debugging Orba2 artipreset, to be sure which sample is played on which note.
# after replacing samples, orba will talk the sample name.
# artipreset is modified to have a static pitch to be able to hear the voice

#expected file structure


# preset_to_dissect/Presets/
# preset_to_dissect/SamplePools/

from pydub import AudioSegment
 
from gtts import gTTS 
import hashlib
import sys
import os
import tempfile
# setting path
sys.path.append('.')
sys.path.append('..')
sys.path.append('./dev_helpers')

 
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

def create_temp_file():
    
    tmp_file = tempfile.NamedTemporaryFile(delete=False)    # beware, it will create tmp files and not remove them. 
    tmp_file.close()
    return tmp_file
 
 

ensure_folder('output')

counter = 0
for s in range(0,12):
   
    #print (s)
    # print (f"{s.name} {s.fileName}")
 

    language = 'en'
 
    text = str(s)
 
    tts = gTTS(text=text, lang=language, slow=False) 
    temp_mp3 = create_temp_file()                 
    tts.save(temp_mp3.name+".mp3")
    sound = AudioSegment.from_mp3( temp_mp3.name+".mp3" )

    filename=f"TEST_{text}_{md5sum(text)}.wav"
    sound.export(f"output/TEST_{text}_{md5sum(text)}.wav", format="wav")

 

    sampledsound=f"""
    	<SampledSound sampleIndex="{counter}" name="{text}" loopStart="0" loopEnd="0" pitch="-2" fileName="{filename}" subdirectory="TEST_SUB" pool="User"></SampledSound>
    """
    counter+=1

    print (sampledsound)