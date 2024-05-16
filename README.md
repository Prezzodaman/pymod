# Pymod
An Amiga module player/renderer written in Python! It uses PyAudio for real-time playback, so you'll need to install PortAudio for it to work. The actual rendering routine only uses 2 of Python's standard libraries (Random and Time), but it can be adapted to work without.

I've included a bunch of test modules that I made myself; they're free for anyone to use, for testing their players.

## Features
* *It can play "Ode to ProTracker" and "Black Queen" perfectly the whole way through!!*
* Rendering to a 16-bit .wav file of any sample rate
* Rendering each channel to its own file
* Real-time playback of modules, with a display of the pattern as it's being played
* Support for modules with any number of channels, from 1 to 99
* Different playback modes (hard-panned stereo, "soft-panned" stereo, and mono)
* Support for uncommon effects such as EFx (invert loop), E5x (set finetune) and 8xx/E8x (set panning)
* An information display, including loop points, finetunes and sample names
* Lots of ProTracker's behaviours are here, including:
    * Line breaks and position breaks together (reverse modules will play just fine)
    * Sample numbers on their own controlling the volume
    * Note cuts alongside sample numbers
    * The ProTracker sine table, used for vibrato and tremolo
    * Per-channel pattern loops
    * The oddly specific sample offset behaviour (check the code for a description)
    * Portamentos and volume slides being unaffected by pattern delays
    * Authentic arpeggio behaviour (period wraparound, "sample cutting" and missed notes)
    * Accurate "invert loop" implementation, using the patented ProTracker Funk Table&trade;

## Installation

pymod requires at least [Python](https://python.org) 3.8. You can install it by installing [pip](https://packaging.python.org/en/latest/tutorials/installing-packages/) and typing the following in a terminal window:

```console
pip install pymod
```

You will also need to install [portaudio](https://www.portaudio.com). On macOS you can do this via [brew](https://brew.sh):

```console
brew install portaudio
```

## Usage

pymod can be used to play a module from the command line:
```console
pymod <options> <path to .mod file> <sample rate> <play mode>
```

- `sample rate` is the rate at which the module is played or rendered.
- `play mode` is either:
    * `info` : Just display info on the module.
    * `test` : Display the module text (list of samples names where mod authors often hide info text).
    * `mono` or `mono_filter` : play/render the module in mono. With or without filter enabled.
    * `stereo_soft` or `stereo_soft_filter` : play/render the module with a soft/partial stereo separation. With or without filter enabled.
    * `stereo_hard` or `stereo_hard_filter` : play/render the module with a hard stereo separation. With or without filter enabled.
- `options` can be:
    * `--render=<path to wav file>` : Renders the module to a wave file. If rendering multiple channels, end the filename with _1 (e.g. pymod_1.wav) and the files will be numbered sequentially.
    * `--loops=<number of loops>` : The amount of times to loop the module.
    * `--verbose` : If playing, this displays the pattern as it's being played. If rendering, this shows the progress of each pattern.
    * `--channels` : Renders each channel to its own file. If playing, this does nothing.
    * `--buffer` : Change the buffer size for realtime playback (default is 1024).

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
    module.render_to(<path_to_wav_file_to_render_to>, <optional flag to render channels separatly>)
```

The `Module` instance also has these methods:

- `set_sample_rate(<rate>)` : Set the rate at which the module is played or rendered.
- `set_nb_of_loops(<nb_of_loops>)` : Set the amount of times to loop the module.
- `set_play_mode(<play_mode>)` : Set the play mode, similar the values used by the command line version.
- `set_verbose(<flag>)` : If playing, this displays the pattern as it's being played. If rendering, this shows the progress of each pattern.
- `set_buffer_size(<size>)` : Change the buffer size for realtime playback (default is 1024).


## Remarks
* Rendering can be quite slow ("Ode to ProTracker" at 48k in mono takes 23 seconds), but during real-time playback, it's fast enough, unless the module has lots of channels.
* The sample rate has a surprising effect on the quality of samples! Higher sample rates will sound better, but it'll use a lot more processing time. 48000 Hz is recommended!
* The filter "simulation" is far from perfect; it's very subtle, but it's there. I have no plans to make it accurate, as E0x is almost never used. It's only here for the sake of completion!
* Rendering channels individually will take much longer. For example, a 4 channel module will take 4x as long, as it goes through the whole module for each channel. It's done this way so it uses less RAM, instead of storing all the channels at once.

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

## Thanks
* **The developers of OpenMPT** - For getting me started tracking way back in 2016, and making the one piece of software I use every day for all of my music (I owe a lot to you!)
* **ModArchive.org** - For being an invaluable resource to the tracking community
* **FireLight** - For creating "fmoddoc2.zip", the best source of information for writing module players!
* **Warren Willmey** - For documenting some overlooked ProTracker quirks for Weasel Audio Library, and making some very useful test modules
* **The tracking community** - For being so creative :)
