## 1.1.0
### General notes
* Pymod is now a PyPI compatible module (!) and split into multiple source files
* The code no longer runs in a While loop - it can now be used in other programs and uses a significantly neater (and more sensible) object-oriented approach
* More consistent syntax throughout the code
    * Improved overall code quality (e.g. syntax that complies better to the PEP-8 standard, and usage of f-strings... finally...)
* Added a visual "loops" counter for command-line playback
* Added the current channel/loops when rendering without the verbose flag
* Added a quiet mode that gives no feedback when rendering (useful for batch renders)
* Simplified the way channels are rendered individually
* Prevented file rendering to an extension other than .wav
* Added support for ProTracker modules with more than 64 patterns (see test module "howmanypatterns.mod")
    * Order length is still limited to 128 patterns, but that's a constraint within ProTracker itself (longer orders are still technically possible)
* Added a "legacy" mode that simulates ProTracker 2.3's quirks
* Added an extended period table featuring 2 extra octaves, nabbed from TakeTracker (used by default)
* When rendering modules using the filter, each channel is filtered individually, instead of the sum
    * The files SOUNDED okay, but because the overall sum was filtered, there were slight differences when comparing a mix of the rendered channels against a mixed file rendered by Pymod
* Pymod-exclusive effects have been added!
    * E02 can be used on a channel to roll off the high-end for that channel, reducing audible ringing from bass sounds! The filter can be turned off using effect E03 (see the test module "basschan.mod" for an example)
    * E04 and E05 can be used to add a sort of pseudo-reverb effect to a channel, with a fast or slow decay respectively! This can be turned off using effect E06; the effect will decay instead of cutting off (see the test module "delayfx.mod" for an example)
    * E07 and E08 can be used to play a sample backwards or forwards respectively (see the test module "reverse.mod" for an example)
    * These effects will use up more processing time, so for real-time playback, it's highly advisable to increase the buffer size for less jitter!
* Added an "amplify" option which increases/decreases the rendering/playback volume
* ProTracker 2.3's loop behaviour is implemented (see test module "loopchange.mod")
	* A sample number by itself will change the currently looping sample. So if another sample number is encountered while a sample is looping, the loop of the other sample will be played (starting from its loop point) once the current one has reached the loop end point
	* If a sample's loop starts at 0, it should first play through all the way (including after the loop end) before playing the looped section
* Sample summing is now handled sensibly (bytes are only converted once all bytes are summed together)
* The current progress is now shown while rendering (as a percentage)
	* When playing, this remaining time will be shown alongside the elapsed time
* The estimated length of the module is now shown when viewing the module info!
* Sample rate is now optional, and defaults to 44100 Hz
* Sample interpolation has now been added as an option, resulting in much cleaner samples!

### Legacy mode
An option new to version 1.1.0, this mode enforces many of ProTracker 2.3's quirks.

The documentation for Weasel Audio Library (https://weaselaudiolib.sourceforge.net/TakeTracker-FastTracker-notes-and-format.html) documents ProTracker's quirks extremely well and was used extensively as a reference. Also, OpenMPT's test modules are extremely valuable (https://wiki.openmpt.org/Development:_Test_Cases) and cover yet more of ProTracker's behaviours.

The quirks mentioned below are only affected in legacy mode, otherwise, they behave as generally expected...
* Arpeggios are now ProTracker accurate (see test module "arptimings.mod")
    * Arpeggio wraparounds are also accurate (see test modules "wraparound.mod", "wraparound2.mod" and "timestretch.mod")
    * It's worth noting that when exploiting arpeggio wraparounds for the "cutting" effect, the period timing can be slightly off (see "arpdesync.mod", although if you compare it to different replayers, they're all slightly different!)
    * BUT... in doing this, the duff note at the end of "ode2ptk.mod" is now present, which believe it or not, is technically the correct behaviour!
* Vibrato/tremolo waveforms now behave exactly as they do in ProTracker (using the default values on every first tick)
* Legacy mode uses the standard ProTracker period table instead
* Using a line break alongside a pattern delay will offset the specified line by 1 (see test module "delayskip.mod")
* Portamentos constrain to the "maximum" and "minimum" period values (see test module "portlimit.mod")
    * They're ACTUALLY the maximum and minimum values of the default finetune, not overall. That's just ProTracker for you!
* Note retriggers are now 100% accurate!
    * Notes will retrigger if the current tick % retrigger speed is 0... BUT if there's a note alongside it, then the sample will be ignored on the first tick of each line (apart from the initial playback of the note). ProTracker, man.
* The weirdly specific ProTracker behaviour when using LOOPED samples alongside the note delay effect
    * If the sample is looping and the note delay is used, the last period is used and the sample is swapped on the first tick, but once the note delay is reached, the specified period is finally used

### Bug fixes
* Fixed a bug with note delays being greater than the ticks per line, resulting in the note still playing
* Fixed a bug with note cuts being greater than the ticks per line, resulting in any further notes cutting incorrectly
* Fixed a bug where a position breaking to itself wouldn't immediately count as a loop (fixes the test modules "delaysim.mod" and "breaks2.mod")
* Fixed a bug where setting the finetune (using E5x) would only work if the value wasn't 0
* Fixed file rendering to parent/subdirectories
* "ode2ptk.mod" now renders correctly to individual channels
* Loop detection has been significantly improved:
	* Fixed duplicate loops (test modules "line.mod", "simpy.mod" and "patdelay.mod" now loop properly)
	* Fixed loop detection for "ode2ptk.mod", the test module "delayskip.mod", and any modules that return to the beginning without a position/line break
	* Fixed loop detection when line breaking in a module that's only 1 order long (fixes the test module "patdelay.mod")
	* Fixed loop detection when breaking to a line that's already been visited (fixes the test modules "line.mod" and "volslide2.mod")
* Fixed a slight bug in the offset effect (see the test module "offsetness.mod")
* Mono renders are no longer extremely quiet
* Fixed the offset effect being 255 bytes behind

### To do
* Perhaps figure out a way of rendering only a few samples (small buffer size) at a time, allowing for real-time playback to be used alongside other Python code
* Fix sample swapping behaviour with empty samples
* Figure out unit testing for legacy mode

## 1.0.1:
### Bug fixes
* Partially fixed an offset issue with "ode2ptk.mod" when rendering individual channels
* Kept the volume identical when rendering individual channels
* Fixed an issue when using the --channels/-c option and not rendering, causing the module to play indefinitely