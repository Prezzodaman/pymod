# Pymod
An Amiga module player/renderer written in Python! It uses PyAudio for real-time playback, so you'll need to install PortAudio for it to work (more information below). I've included a bunch of test modules that I made myself; they're free for anyone to use, for testing their players.

## Features
* *It can play "Ode to ProTracker" and "Black Queen" perfectly the whole way through!!*
* Rendering to a 16-bit .wav file of any sample rate
* Rendering each channel to its own file
* Real-time playback of modules, with a display of the pattern as it's being played
* Support for modules with any number of channels, from 1 to 99
* Support for modules with more than 65 patterns
* Different playback modes (hard-panned stereo, "soft-panned" stereo, and mono)
* Support for uncommon effects such as EFx (invert loop), E5x (set finetune) and 8xx/E8x (set panning)
* An information display, including loop points, finetunes and sample names
* A crude simulation of the Amiga's filter (E0x works here!)
* Lots of ProTracker's behaviours are here, including:
	* Line breaks and position breaks together (reverse modules will play just fine)
	* Sample numbers on their own controlling the volume
	* Note cuts alongside sample numbers
	* The ProTracker sine table, used for vibrato and tremolo
	* Per-channel pattern loops
	* The oddly specific sample offset behaviour
	* Portamentos and volume slides being unaffected by pattern delays
	* Accurate "invert loop" implementation, using the patented ProTracker Funk Table&trade;
* A legacy mode that enforces ProTracker 2.3's quirks, including:
	* Vibrato and tremolo missing every first tick
	* Authentic arpeggio behaviour (period wraparound, "sample cutting" and missed notes)
	* Portamentos (and any out-of-range notes) constraining to ProTracker's period range
	* No panning effects (8xx/E8x do nothing in legacy mode)
	* 4 channel modules only
* An extended note range for modules not made using ProTracker (two extra octaves!)
* Extra effects exclusive to Pymod

## Installation
Pymod requires at least [Python](https://python.org) 3.8. You can install it by installing [pip](https://packaging.python.org/en/latest/tutorials/installing-packages/) and typing the following in a terminal window:

```console
pip install pymod
```

You will also need to install [portaudio](https://www.portaudio.com), which is required by PyAudio. On macOS you can do this via [brew](https://brew.sh):

```console
brew install portaudio
```

## Usage
Pymod can be used to play a module from the command line:
```console
pymod <options> <path to .mod file> <sample rate> <play mode>
```

- `sample rate` is the sample rate at which the module is played or rendered.
- `play mode` can be one of the following:
	* `info` : Just display info about the module.
	* `text` : Display the module text (list of sample names where mod authors often hide info text).
	* `mono` or `mono_filter` : Play/render the module in mono (with or without filter enabled)
	* `stereo_soft` or `stereo_soft_filter` : Play/render the module with a soft/partial stereo separation (with or without filter enabled)
	* `stereo_hard` or `stereo_hard_filter` : Play/render the module with a hard stereo separation (with or without filter enabled)
- `options` can be:
	* `--render <path to wav file> (-r)` : Renders the module to a wave file. If rendering multiple channels, end the filename with _1 (e.g. pymod_1.wav) and the files will be numbered sequentially.
	* `--loops <number of loops> (-l)` : The amount of times to loop the module. If this option isn't specified, the module will play once.
	* `--verbose (-v)` : If playing, this displays the pattern as it's being played. If rendering, this shows the progress of each pattern.
	* `--channels (-c)` : Renders each channel to its own file. If playing, this does nothing.
	* `--buffer <buffer size> (-b)` : Change the buffer size for realtime playback (default is 1024).
	* `--quiet (-q)` : Shows absolutely no info while playing/rendering a module.
	* `--amplify <factor> (-a)` : Amplifies the output volume by a certain factor, useful for modules with lots of channels. 1 is normal volume, 2 is double volume, 0.5 is half volume, etc.

Pymod can also be imported into your Python programs and used as a module:

```python
import pymod

module = pymod.Module(<path_to_mod_file>)

if module is not None:
	module.play()
```

or

```python
import pymod

module = pymod.Module(<path_to_mod_file>)

if module is not None:
	module.render_to(<path_to_wav_file_to_render_to>, <optional flag to render channels separately>)
```

The `Module` instance also has these methods:

- `set_sample_rate(<rate>)` : Set the sample rate at which the module is played or rendered.
- `set_nb_of_loops(<nb_of_loops>)` : Set the amount of times to loop the module.
- `set_play_mode(<play_mode>)` : Set the play mode (<play_mode> is a string containing one of the play modes listed above)
- `set_verbose(<flag>)` : If playing, this displays the pattern as it's being played. If rendering, this shows the progress of each pattern.
- `set_buffer_size(<size>)` : Change the buffer size for realtime playback (default is 1024).
- `set_quiet(<flag>)` : If true, this shows absolutely no info while playing/rendering a module.
- `set_amplify(<factor>)` : Amplifies the output volume by a certain factor.

By default, the sample rate is 44100 Hz and the play mode is mono. These can be changed on init by specifying the optional arguments `sample_rate` and `play_mode`. `verbose`, `quiet` and `amplify` can also be specified as arguments.

## Unit testing
Unit tests can be run by using `pytest`. These tests run against a set of pre-generated wav files to make sure that the output is consistent across changes.

These test files can be re-generated, when a change requires it, by running Python in interactive mode from the project's root folder and typing:
```
import sys
import os
sys.path.insert(0, os.getcwd())
import pymod
pymod.Module._generateTestFiles()
```

## Remarks
* Rendering/playback can be quite slow, but it's fast enough during real-time playback, unless the module has lots of channels. If there's noticable jitter, use the --buffer/-b option to change the buffer size.
* The sample rate has a surprising effect on the quality of samples! Higher sample rates will sound better, but it'll use a lot more processing time.
* The filter "simulation" is far from perfect; it's very subtle, but it's there. I have no plans to make it accurate, as E0x is almost never used. It's only here for the sake of completion!
* Rendering channels individually will take much longer. For example, a 4 channel module will take 4x as long, as it goes through the whole module for each channel. It's done this way so it uses less RAM, instead of storing all the channels at once.
	* The individual files will be at the same volume as if playing a module normally, so when mixed together, the result will be identical!

## Supported effects
* **0xy** - Arpeggio
* **1xx** - Portamento up
* **2xx** - Portamento down
* **3xx** - Tone portamento (+ memory)
* **4xy** - Vibrato (+ memory)
* **5xx** - Volume slide + tone portamento
* **6xx** - Volume slide + vibrato
* **7xy** - Tremolo (+ memory)
* **8xy** - Set panning
* **9xx** - Sample offset (+ memory)
* **Axy** - Volume slide
* **Bxx** - Position break
* **Cxx** - Set volume
* **Dxx** - Line break
* **E0x** - Filter on/off
* **E1x** - Fine portamento up
* **E2x** - Fine portamento down
* **E3x** - Glissando control
* **E4x** - Vibrato waveform (+ retrigger)
* **E5x** - Set finetune
* **E6x** - Pattern loop
* **E7x** - Tremolo waveform (+ retrigger)
* **E8x** - Set panning
* **E9x** - Retrigger note
* **EAx** - Fine volume slide up
* **EBx** - Fine volume slide down
* **ECx** - Note cut
* **EDx** - Note delay
* **EEx** - Pattern delay
* **EFx** - Invert loop

## Pymod exclusive effects
Note: in legacy mode, these will do nothing!
* **E02** - Channel bass filter on
* **E03** - Channel bass filter off

## Thanks
* **The developers of OpenMPT** - For getting me started tracking way back in 2016, and making the one piece of software I use every day for all of my music (I owe a lot to you!)
* **ModArchive.org** - For being an invaluable resource to the tracking community
* **FireLight** - For creating "fmoddoc2.zip", the best source of information for writing module players!
* **Warren Willmey** - For documenting some overlooked ProTracker quirks for Weasel Audio Library, and making some very useful test modules
* **Didier Malenfant** - For helping generously and doing the unthinkable: helping turn Pymod into a useable module! (no, not that kind)
* **The tracking community** - For being so creative :)
