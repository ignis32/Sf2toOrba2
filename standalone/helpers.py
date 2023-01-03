import slugify
import tempfile
import os
from os.path import exists
import random
import string
import hashlib

temp_files_to_remove = []

def note_to_text(number: int):
    OCTAVE_SHIFT=0
    NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    NOTES_IN_OCTAVE = len(NOTES)
    octave = number // NOTES_IN_OCTAVE
    note = NOTES[number % NOTES_IN_OCTAVE]
    return f"{note}{octave+OCTAVE_SHIFT}"    # with  OCTAVE_SHIFT=0 it will use C5 as middle C.

def note_to_pitch(midi_note, fine_tuning_cents = 0 , coarse_tuning_semitones = 0, sample_rate = 48000, midi_key_pitch_influence = 0):
    OCTAVE_SHIFT=0
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
    return  round(pitch,6)
    


# def create_temp_wav_file(name):
    
#     tmp_wav_file = tempfile.NamedTemporaryFile(prefix = f"sf2toOrba2.{name}.", suffix= ".tmp.wav",delete=False)  
#     temp_files_to_remove.append(tmp_wav_file.name)  # remember all the temporary files to remove them before ending script.
#     tmp_wav_file.close()  #actually, I need only file name.
#     return tmp_wav_file

def generate_temp_filepath(slug_name) -> str:
    random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    temp_filepath = os.path.join(tempfile.gettempdir(),  f"SF2_ORBA_{slug_name}_{random_string}.wav")
    if  exists(temp_filepath):
        print(f"wow, what a luck, temporary file with random name {temp_filepath} already exists, trying again.")
        return generate_temp_filepath(slug_name)
    temp_files_to_remove.append(temp_filepath)
    return  temp_filepath



def  remove_temp_files():
    print("removing temporary files")
    for i in temp_files_to_remove:
        print(f"removing tmp file: {i}")
        os.unlink(i)

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
    
def slugify_name(name):
    allowed_pattern=r'[^-a-zA-Z0-9_#()]+' 
    slug_name = slugify.slugify(name, regex_pattern=allowed_pattern, lowercase=False)  # this name is used as a folder name, it should be valid for filesystem
    return slug_name