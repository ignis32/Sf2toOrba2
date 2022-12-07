# Sf2toOrba2
Tool for converting SF2  instruments to Orba2 samples



This is an early PoC, that probably works only for some specific cases.
What it does currently - it tries to export samples from the SF2 instrument library,
tries to guess root notes and loop settings for each played note, and exports samples naming files according to subskybox's naming convention,
to prepare a preset using another script:

https://github.com/subskybox/Orba/blob/master/orba2/orba_sample_set_generator.py

