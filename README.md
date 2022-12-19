# Sf2toOrba2
Helpers  for converting SF2 instruments samples, for Orba2 custom preset creation. 




sf2_to_subskybox_to_orba2/extract_samples_from_sf2_to_subskybox.py   - script that is supposed to work in pair with Subskybox's script. Extracts samples from sf2 to wav files, and fills wav files names with  pitch/velocity data.  


standalone/Orbapreset.py   -  library for parsing artipreset into python object hierarchy, that can be modified and stored back to xml form.


standalone/test_orba_library_primitives.py  - small and ugly demo of using OrbaPreset library
standalone/test_xml_differences.py - script  I used to verify parsing validity of the  OrbaPreset library