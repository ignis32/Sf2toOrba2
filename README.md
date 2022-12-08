# Sf2toOrba2
Helper  for converting SF2 instruments samples for Orba2 custom preset creation. 

This is an early PoC, that probably works only for some specific cases.
What it does currently - it tries to export samples from the SF2 instrument library,
tries to guess root notes and loop settings for each played note, and exports samples naming files according to subskybox's naming convention,
to prepare a preset xml using another script:

https://github.com/subskybox/Orba/blob/master/orba2/orba_sample_set_generator.py


## Dependencies

requires **sf2utils, python-slugify** libraries.


## Known issues:

Export is driven from "generators" of SF2. This might cause multiple exports of the same sample under different filenames when the same sample is used in different generators.

e.g,:

If the same sample is explicitly binded to the different velocity ranges it will be exported multiple times.
This might be a problem for SF2 instruments that use velocity for alternation between samples, to provide playing "pseudo random" sample variants.
(for example, each even velocity plays sample 1 and each odd velocity plays sample 2)

If same sample is explicitly binded to different note ranges - multiple export will happen too.

## What is implemented:
    
mutiple instruments export is implemented.

root note for each sample is calculated from the sample default root note and override root note.

loop start and end are extracted.  will be both 0 if no loop.

velocity range top value is extracted

uuid is generated from instrument_name, root note, and velocity



## Samples are exported as below:

    SF2-<Instrument name>_<Note>_<Velocity range top>_<LoopStart>_<LoopEnd>_<UUID>.wav     

## What is not implemented:

Sample related quite vital stuff that might affect resulting orba preset consistency:

* Sample pitch tuning is ignored 
* Key range is ignored (only root note information is used)



* Modulators are ignored
* Envelopes are ignored
* Presets are ignored (have no idea how to translate that to orba)
* Effects are ignored 

## TBD

real:

* command line arguments
* direct orba sample set generation
* sample rate detection and corresponding pitch correction


fantasies:

* orba preset template generation (haha, that will take a while)
* try to bind modulators/effects/envelopes to their Orba equialents. (need more orba preset reverse engineering for that)
* preset upload


