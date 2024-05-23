#
# Copyright (c) 2023-present Presley Peters (Prezzo).
#
# This file is part of pymod.
#
# pymod is free software: you can redistribute it and/or modify it under the terms of the GNU General
# Public License as published by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pymod is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
# License for more details.
#
# You should have received a copy of the GNU General Public License along with pymod. If not,
# see <https://www.gnu.org/licenses/>.
#

import wave
import time
import pyaudio
import random
import os

from .__about__ import __version__

# 2.0.0:
#   General notes:
#      Now version 2.0.0, because the entire codebase has changed, and lots of bugs have been fixed!
#         Pymod is now a PyPI compatible module (!) and split into multiple source files
#         The code no longer runs in a While loop - it can now be used in other programs and uses a significantly neater (and more sensible) object-oriented approach
#      More consistent syntax throughout the code
#         Improved overall code quality (e.g. syntax that complies better to the PEP-8 standard, and usage of f-strings... finally...)
#      Added a visual "loops" counter for command-line playback
#      Added the current channel/loops when rendering without the verbose flag
#      Added a quiet mode that gives no feedback when rendering (useful for batch renders)
#      Removed a bunch of redundant, useless code involving rendering to individual channels
#      Prevented file rendering to an extension other than .wav
#
#   Bugs fixed:
#      Fixed a bug with note delays being greater than the ticks per line, resulting in the note still playing
#      Fixed a bug with note cuts being greater than the ticks per line, resulting in any further notes cutting incorrectly
#      Arpeggio wraparounds are now significantly more accurate (see test modules "wraparound.mod" and "wraparound2.mod")
#         BUT... in doing this, the duff note at the end of "ode2ptk.mod" is now present, which believe it or not, is ProTracker accurate!
#      Fixed a bug where a position breaking to itself wouldn't immediately count as a loop (fixes the test modules "delaysim.mod" and "breaks2.mod")
#      Fixed file rendering to parent/subdirectories
#      Fixed duplicate loops (test modules "line.mod", "simpy.mod" and "patdelay.mod" now loop properly)
#
#   To do:
#      Investigate why rendering "ode2ptk.mod" to individual channels causes channels 2-4 to be slightly later, even though it's still rendering the module as usual
#      Perhaps figure out a way of rendering only a few samples (small buffer size) at a time, allowing for real-time playback to be used alongside other Python code
#      Add interpolated playback/rendering (processing the module at double the specified sample rate, then averaging the current and last bytes to reduce ringing)
#         This will, of course, add lots of overhead when playing in real-time, so this is only to be considered...
#      Calculate module rendering/playing progress (e.g. percentage rendered)

# 1.0.1:
#   Bugs fixed:
#      Partially fixed an offset issue with "ode2ptk.mod" when rendering individual channels
#      Kept the volume identical when rendering individual channels
#      Fixed an issue when using the --channels/-c option and not rendering, causing the module to play indefinitely


# -- Classes
class Module:
    """Python class that plays/renders ProTracker modules using PyAudio."""

    # -- Class Variables
    _mod_periods = [
        [  # no finetune
            856, 808, 762, 720, 678, 640, 604, 570, 538, 508, 480, 453,
            428, 404, 381, 360, 339, 320, 302, 285, 269, 254, 240, 226,
            214, 202, 190, 180, 170, 160, 151, 143, 135, 127, 120, 113
        ],
        [  # finetune  + 1
            850, 802, 757, 715, 674, 637, 601, 567, 535, 505, 477, 450,
            425, 401, 379, 357, 337, 318, 300, 284, 268, 253, 239, 225,
            213, 201, 189, 179, 169, 159, 150, 142, 134, 126, 119, 113
        ],
        [  # + 2
            844, 796, 752, 709, 670, 632, 597, 563, 532, 502, 474, 447,
            422, 398, 376, 355, 335, 316, 298, 282, 266, 251, 237, 224,
            211, 199, 188, 177, 167, 158, 149, 141, 133, 125, 118, 112
        ],
        [  # + 3
            838, 791, 746, 704, 665, 628, 592, 559, 528, 498, 470, 444,
            419, 395, 373, 352, 332, 314, 296, 280, 264, 249, 235, 222,
            209, 198, 187, 176, 166, 157, 148, 140, 132, 125, 118, 111
        ],
        [  # + 4
            832, 785, 741, 699, 660, 623, 588, 555, 524, 495, 467, 441,
            416, 392, 370, 350, 330, 312, 294, 278, 262, 247, 233, 220,
            208, 196, 185, 175, 165, 156, 147, 139, 131, 124, 117, 110
        ],
        [  # + 5
            826, 779, 736, 694, 655, 619, 584, 551, 520, 491, 463, 437,
            413, 390, 368, 347, 328, 309, 292, 276, 260, 245, 232, 219,
            206, 195, 184, 174, 164, 155, 146, 138, 130, 123, 116, 109
        ],
        [  # + 6
            820, 774, 730, 689, 651, 614, 580, 547, 516, 487, 460, 434,
            410, 387, 365, 345, 325, 307, 290, 274, 258, 244, 230, 217,
            205, 193, 183, 172, 163, 154, 145, 137, 129, 122, 115, 109
        ],
        [  # + 7
            814, 768, 725, 684, 646, 610, 575, 543, 513, 484, 457, 431,
            407, 384, 363, 342, 323, 305, 288, 272, 256, 242, 228, 216,
            204, 192, 181, 171, 161, 152, 144, 136, 128, 121, 114, 108
        ],
        [  # finetune -8
            907, 856, 808, 762, 720, 678, 640, 604, 570, 538, 508, 480,
            453, 428, 404, 381, 360, 339, 320, 302, 285, 269, 254, 240,
            226, 214, 202, 190, 180, 170, 160, 151, 143, 135, 127, 120
        ],
        [  # -7
            900, 850, 802, 757, 715, 675, 636, 601, 567, 535, 505, 477,
            450, 425, 401, 379, 357, 337, 318, 300, 284, 268, 253, 238,
            225, 212, 200, 189, 179, 169, 159, 150, 142, 134, 126, 119
        ],
        [  # -6
            894, 844, 796, 752, 709, 670, 632, 597, 563, 532, 502, 474,
            447, 422, 398, 376, 355, 335, 316, 298, 282, 266, 251, 237,
            223, 211, 199, 188, 177, 167, 158, 149, 141, 133, 125, 118
        ],
        [  # -5
            887, 838, 791, 746, 704, 665, 628, 592, 559, 528, 498, 470,
            444, 419, 395, 373, 352, 332, 314, 296, 280, 264, 249, 235,
            222, 209, 198, 187, 176, 166, 157, 148, 140, 132, 125, 118
        ],
        [  # -4
            881, 832, 785, 741, 699, 660, 623, 588, 555, 524, 494, 467,
            441, 416, 392, 370, 350, 330, 312, 294, 278, 262, 247, 233,
            220, 208, 196, 185, 175, 165, 156, 147, 139, 131, 123, 117
        ],
        [  # -3
            875, 826, 779, 736, 694, 655, 619, 584, 551, 520, 491, 463,
            437, 413, 390, 368, 347, 328, 309, 292, 276, 260, 245, 232,
            219, 206, 195, 184, 174, 164, 155, 146, 138, 130, 123, 116
        ],
        [  # -2
            868, 820, 774, 730, 689, 651, 614, 580, 547, 516, 487, 460,
            434, 410, 387, 365, 345, 325, 307, 290, 274, 258, 244, 230,
            217, 205, 193, 183, 172, 163, 154, 145, 137, 129, 122, 115
        ],
        [  # -1
            862, 814, 768, 725, 684, 646, 610, 575, 543, 513, 484, 457,
            431, 407, 384, 363, 342, 323, 305, 288, 272, 256, 242, 228,
            216, 203, 192, 181, 171, 161, 152, 144, 136, 128, 121, 114
        ]
    ]

    _mod_arp_period_cap = _mod_periods[0][-1]  # the highest note (lowest period) of the default finetune

    _mod_sine_table = [
        0, 24, 49, 74, 97, 120, 141, 161,
        180, 197, 212, 224, 235, 244, 250, 253,
        255, 253, 250, 244, 235, 224, 212, 197,
        180, 161, 141, 120, 97, 74, 49, 24
    ]

    # the protracker sine table is only half a wave, so we're completing it here
    for a in range(0, len(_mod_sine_table)):
        _mod_sine_table.append(0 - _mod_sine_table[a])

    _mod_funk_table = [  # this sounds like something i made up, but it's actually called the funk table :D
        0, 5, 6, 7, 8, 10, 11, 13, 16,
        19, 22, 26, 32, 43, 64, 128
    ]

    # -- Class Methods
    @classmethod
    def _generateTestFiles(cls):
        """Generate all the test files used to compare against in the uniot tests.
           This should only be used in a local repo and not with an installed module."""

        source_folder = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
        modules_folder = os.path.join(source_folder, "tests", "modules")
        wavs_folder = os.path.join(source_folder, "tests", "wavs")

        if not os.path.exists(modules_folder) or not os.path.exists(wavs_folder):
            print("Error: This should be used on a local repo, not an installed module.")
            return

        for filename in os.listdir(modules_folder):
            module_file_path = os.path.join(modules_folder, filename)
            if not os.path.isfile(module_file_path) or not os.path.splitext(filename)[1] == ".mod":
                continue

            module = Module(module_file_path)
            assert module is not None

            # -- This makes sure the random offset value used in some effect matches
            # -- the one used during unit testing.
            random.seed(Module.render_test_random_seed())

            module.set_sample_rate(Module.render_test_sample_rate())
            module.set_play_mode("stereo_hard")
            module.set_quiet(True)

            base_name = os.path.basename(module_file_path)
            print(f"Rendering {base_name}...")
            module.render_to(os.path.join(wavs_folder, os.path.splitext(filename)[0] + ".wav"))

    @classmethod
    def _mod_get_frequency(cls, period):
        if period > 0:
            return 7093789 / (period * 2)
        else:
            return 0

    @classmethod
    def _mod_get_period_note(cls, period):  # returns the note value
        note = -1
        found = False
        for period_set in Module._mod_periods:
            if period in period_set and not found:
                note = period_set.index(period)
                found = True
        return note

    @classmethod
    def _mod_get_finetune_period(cls, period, finetune):
        period_found = Module._mod_periods[finetune][Module._mod_get_period_note(period)]
        if period_found < Module._mod_arp_period_cap:
            period_found = Module._mod_arp_period_cap
        return period_found

    @classmethod
    def _mod_get_closest_period(cls, period, finetune):
        differences = []
        for period_2 in Module._mod_periods[finetune]:
            differences.append(abs(period - period_2))
        return Module._mod_periods[finetune][differences.index(min(differences))]

    @classmethod
    def _get_panned_bytes(cls, byte, pan):  # expects an unsigned byte between 0 and 65535. pan value is between -1 and 1 (left and right)
        return int((byte - 32768) * ((pan / 2) - 0.5)), 0 - int(((byte - 32768) * ((pan / 2) + 0.5)))

    @classmethod
    def play_modes(cls):
        play_modes = ["mono", "stereo_soft", "stereo_hard"]

        for a in range(0, len(play_modes)):
            play_modes.append(play_modes[a] + "_filter")

        play_modes.extend(["info", "text"])

        return play_modes

    @classmethod
    def buffer_size_default(cls):
        return 1024

    @classmethod
    def render_test_sample_rate(cls):
        return 22050

    @classmethod
    def render_test_random_seed(cls):
        return 23

    # -- Instance Methods
    def __init__(self, input_file_path, sample_rate=44100, play_mode="mono", verbose=False, quiet=False):
        """Constructor based on command line arguments."""

        self._mod_tempo = 125
        self._mod_ticks = 6

        self._input_file = input_file_path
        self._sample_rate = sample_rate
        self._render_file = None
        self._loops = False
        self._render_channels = False
        self._play_mode = play_mode
        self._verbose = verbose
        self._buffer_size = Module.buffer_size_default()
        self._quiet = quiet  # this only affects the program's "introduction", playback and rendering - showing module info will still work

    # https://modarchive.org/forums/index.php?topic=2709.0
    def _mod_get_tempo_length(self):
        return (2500 / self._mod_tempo) * (self._sample_rate / 1000)

    def _run(self):
        if self._input_file is None:
            print("Error: Missing module filename!")

        if self._loops is None:
            self._loops = 1
        else:
            self._loops += 1

        if not self._quiet:
            print(f"Pymod v{__version__}")
            print("by Presley Peters, 2023-present")
            print()

        with open(self._input_file, "rb") as file:
            mod_file = bytearray(file.read())  # we're converting to a bytearray so the "invert loop" effect works (byte objects are immutable)

        mod_ms_per_tick = self._mod_get_tempo_length()
        mod_ticks_counter = 0

        mod_channels = 0
        mod_type = ""
        for a in range(1080, 1084):
            mod_type += chr(mod_file[a])
        if mod_type == "M.K.":
            mod_channels = 4
            mod_type_string = "ProTracker (or generic module tracker)"
        if mod_type.endswith("CHN"):
            try:
                mod_channels = int(mod_type[:1])
                mod_type_string = "Generic module tracker"
            except Exception:  # not an integer...
                pass  # ...mod_channels will remain 0, and the appropriate error will be returned
        if mod_type.endswith("CH"):
            try:
                mod_channels = int(mod_type[:2])
                mod_type_string = "Generic module tracker"
            except Exception:
                pass
        elif mod_type.startswith("TDZ"):
            try:
                mod_channels = int(mod_type[-1])
                mod_type_string = "TakeTracker"
            except Exception:
                pass
        mod_channels_adjusted = mod_channels
        if mod_channels % 2 == 1 and mod_channels > 1:
            mod_channels_adjusted += 1

        if mod_channels == 0:
            print("Error: Invalid module!")
        elif self._sample_rate < 1000 or self._sample_rate > 380000:
            print("Error: Sample rate must be between 1000 and 380000!")
        elif self._play_mode not in Module.play_modes():
            play_modes_string = ", ".join(Module.play_modes())
            print(f"Error: Invalid play mode: {self._play_mode}. Accepted modes: {play_modes_string}")
        elif self._buffer_size < 0 or self._buffer_size > 8192:
            print("Error: Buffer size must be between 0 and 8192!")
        elif self._render_file is not None and self._render_channels and not self._render_file.endswith("_1.wav"):
            print("Error: File name is suffixed incorrectly for channel rendering!")
        elif self._render_file is not None and os.path.splitext(self._render_file)[-1].lower() != ".wav":
            print("Error: Output must be a .wav file!")
        elif self._render_file is None and self._render_channels:
            print("Error: The --channels/-c option can only be used alongside the --render/-r option!")
        else:
            stereo = self._play_mode.startswith("stereo")
            mod_lines = 64

            mod_name = ""
            for a in range(0, 20):
                mod_name += chr(mod_file[a])

            mod_pointer = 20
            mod_samples_amount = 31
            mod_unique_samples = []
            mod_samples = []
            for a in range(0, mod_samples_amount):
                sample = {}
                sample_name = ""
                for b in range(0, 22):
                    if mod_file[mod_pointer] != 0:
                        sample_name += chr(mod_file[mod_pointer])
                    mod_pointer += 1

                sample_length = (mod_file[mod_pointer + 1] | (mod_file[mod_pointer] << 8)) * 2
                mod_pointer += 2

                sample_finetune = mod_file[mod_pointer]
                mod_pointer += 1

                sample_volume = mod_file[mod_pointer]
                mod_pointer += 1

                sample_loop_start = (mod_file[mod_pointer + 1] | (mod_file[mod_pointer] << 8)) * 2
                mod_pointer += 2
                sample_loop_length = (mod_file[mod_pointer + 1] | (mod_file[mod_pointer] << 8)) * 2
                mod_pointer += 2

                sample.update({"name": sample_name})
                sample.update({"length": sample_length})
                sample.update({"finetune": sample_finetune})
                sample.update({"volume": sample_volume})
                sample.update({"loop_start": sample_loop_start})
                sample.update({"loop_length": sample_loop_length})
                mod_samples.append(sample)
                if sample_length > 0:
                    mod_unique_samples.append([a, sample])

            mod_song_length = mod_file[mod_pointer]
            mod_pointer += 2

            mod_pattern_amount = 0
            mod_order = []
            for a in range(0, 128):
                order = mod_file[mod_pointer]
                mod_order.append(order)
                if order > mod_pattern_amount:
                    mod_pattern_amount = order
                mod_pointer += 1
            mod_pointer += 4
            mod_pattern_amount += 1

            mod_pattern_offsets = []
            for a in range(0, mod_pattern_amount):
                mod_pattern_offsets.append(mod_pointer)
                mod_pointer += mod_channels * 4 * mod_lines

            for a in range(0, mod_samples_amount):
                mod_samples[a].update({"offset": mod_pointer})
                mod_pointer += mod_samples[a]["length"]

            if self._play_mode == "info":
                print("Module:")
                print(f"\tName: {mod_name}")
                print(f"\tPatterns: {mod_pattern_amount}")
                order_string = str(mod_song_length) + " order"
                if mod_song_length > 1:
                    order_string += "s"
                print(f"\tLength: {order_string}")
                print(f"\tChannels: {mod_channels} - {mod_type_string}")
                print("Samples:")
                for sample in mod_unique_samples:
                    looping_string = ""
                    if sample[1]["loop_length"] == 2 and sample[1]["loop_start"] == 0:
                        looping_string = "Loop: None"
                    else:
                        looping_string = f"Loop start:{sample[1]['loop_start']}, Loop length: {sample[1]['loop_length']}"
                    finetune = sample[1]["finetune"]
                    if finetune > 7:
                        finetune = finetune - 16
                    sample_number = str(sample[0] + 1).rjust(2, " ")
                    print(f"\t{sample_number}. {sample[1]['name']}")
                    print(f"\t\tLength: {sample[1]['length']}, {looping_string}, Finetune: {finetune}, Volume: {sample[1]['volume']}")
            elif self._play_mode == "text":
                print("Module text:")
                print()
                for sample in mod_samples:
                    print(sample["name"])
            else:
                mod_note_names = []
                mod_note_letters = ["C-", "C#", "D-", "D#", "E-", "F-", "F#", "G-", "G#", "A-", "A#", "B-"]
                for a in range(0, len(Module._mod_periods[0])):
                    mod_note_names.append(mod_note_letters[a % len(mod_note_letters)] + str((a // 12) + 4))

                file_finished = []

                if self._render_file is None:
                    pya = pyaudio.PyAudio()
                    channels = 1
                    if stereo:
                        channels += 1
                    stream = pya.open(format=pyaudio.paInt16, rate=self._sample_rate, output=True, channels=channels, frames_per_buffer=self._buffer_size)

                if self._render_file is None and not self._verbose and not self._quiet:
                    print("Playing...")

                start_time = time.perf_counter()
                channel_sum = 0
                channel_sum_left = 0
                channel_sum_right = 0
                channel_current = 0  # used when rendering individual channels
                while_condition = True
                while while_condition:
                    mod_jumps = [[0, 0]]
                    mod_orders_visited = []
                    # these are here, because when rendering channels, they need to be reset every time
                    mod_filter = self._play_mode.endswith("filter")  # a <crude> "simulation" of the amiga hardware filter (it's a simple one pole low-pass filter - literally just finding the difference between the current and last sum)
                    mod_filter_flag = mod_filter  # unlike mod_filter, this can't be changed
                    mod_period_amount = len(Module._mod_periods[0])

                    mod_channel_byte = [32768] * mod_channels_adjusted  # the current (unsigned) byte in each channel, summed together later on
                    mod_channel_pan = [0] * mod_channels_adjusted  # -1  =  left, 0  =  centre, 1  =  right
                    for a in range(0, mod_channels):
                        if self._play_mode.startswith("stereo_soft"):
                            if a % 4 == 1 or a % 4 == 2:
                                mod_channel_pan[a] = 0.5
                            else:
                                mod_channel_pan[a] = -0.5
                        else:
                            if a % 4 == 1 or a % 4 == 2:
                                mod_channel_pan[a] = 1
                            else:
                                mod_channel_pan[a] = -1
                    mod_sample_offset = [0] * mod_channels
                    mod_sample_position = [0] * mod_channels
                    mod_sample_number = [0] * mod_channels
                    mod_sample_playing = [False] * mod_channels
                    mod_sample_volume = [0] * mod_channels

                    mod_period = [0] * mod_channels
                    mod_raw_period = [0] * mod_channels
                    mod_frequency = [0] * mod_channels
                    mod_effect_number = [0] * mod_channels
                    mod_effect_param = [0] * mod_channels
                    mod_volslide_amount = [0] * mod_channels
                    mod_volslide_fine = [False] * mod_channels  # if true, the volume is slid on the first tick ONLY
                    mod_port_fine = [False] * mod_channels  # same but for fine pitch slides
                    mod_note_cut_ticks = [-1] * mod_channels  # counts down, when it reaches 0, the note is cut. -1 means no cut, -2 means the note is ignored
                    mod_note_delay_ticks = [-1] * mod_channels  # counts down, when it reaches 0, the note is played. -1 means no delay
                    mod_port_amount = [0] * mod_channels
                    mod_tone_period = [0] * mod_channels  # the period we're sliding from
                    mod_tone_sliding = [False] * mod_channels
                    mod_arp_counter = [0] * mod_channels
                    mod_arp_periods = []
                    for a in range(0, mod_channels):
                        mod_arp_periods.append([0, 0, 0].copy())
                    mod_arp_period = [0] * mod_channels
                    mod_vibrato = [False] * mod_channels
                    mod_vibrato_counter = [0] * mod_channels
                    mod_vibrato_offset = [0] * mod_channels  # offsets the period value without actually changing it
                    mod_vibrato_wave = [0] * mod_channels
                    mod_vibrato_retrigger = [True] * mod_channels  # if true, the vibrato counter is reset as usual
                    mod_tremolo = [False] * mod_channels
                    mod_tremolo_counter = [0] * mod_channels
                    mod_tremolo_offset = [0] * mod_channels
                    mod_tremolo_wave = [0] * mod_channels
                    mod_tremolo_retrigger = [True] * mod_channels
                    mod_retrig_speed = [0] * mod_channels
                    mod_retrig_counter = [0] * mod_channels
                    mod_invert_loop_counter = [0] * mod_channels  # 0  =  no inversion
                    mod_invert_loop_position = [0] * mod_channels
                    mod_invert_loop_speed = [0] * mod_channels
                    mod_finetune_temp = [0] * mod_channels  # for the "set finetune" effect, which doesn't directly affect the sample. if there's no effect, this'll contain the default finetune, otherwise, it'll be overridden. this is used when finding the frequency based on the period values, so it's actually very important!
                    mod_glissando = [False] * mod_channels

                    mod_tone_memory = [0] * mod_channels
                    mod_offset_memory = [0] * mod_channels
                    mod_vibrato_memory = [0] * mod_channels
                    mod_tremolo_memory = [0] * mod_channels

                    mod_pattern_loop_start = [-1] * mod_channels  # -1 if there's no loop right now
                    mod_pattern_loop_end = [-1] * mod_channels
                    mod_pattern_loop_counter = [0] * mod_channels  # counts down on every loop
                    mod_pattern_delay = 0  # if 0, there's no delay. if above 0, it counts down. the pattern only plays if this is 0 and mod_pattern_delay_finished is true
                    mod_pattern_delay_finished = True  # if this is false, it waits until the next line to stop advancing the mod pointer (without this flag, it would hang on whatever channel the effect was encountered on)

                    mod_next_position = 0
                    mod_next_line = 0
                    mod_position_break = False
                    mod_line_break = False

                    mod_order_position = 0
                    mod_pointer = mod_pattern_offsets[mod_order[mod_order_position]]
                    mod_line = 0
                    mod_loops = 0  # different to the "loops" variable, this increases until it reaches "loops"
                    # mod_ending = False  # set when the module's looped so many times
                    mod_bpm = 0  # calculated from the tempo and ticks/line (only used for a visual indicator)

                    sample_byte = 32768
                    sample_byte_last = 32768

                    if self._render_channels:
                        while_condition = channel_current < mod_channels - 1
                    else:
                        while_condition = False
                    while mod_order_position < mod_song_length:
                        while mod_line < mod_lines:
                            current_time = time.perf_counter()
                            time_elapsed = int(current_time - start_time)
                            time_elapsed_minutes = time_elapsed // 60
                            time_elapsed_seconds = time_elapsed % 60
                            time_elapsed_string = f"{time_elapsed_minutes}m {time_elapsed_seconds}s"

                            line_string = ""
                            loop_string = ""
                            if self._loops > 1 or self._render_channels:
                                loop_string = " ("
                            if self._loops > 1:
                                loop_string += f"loop {mod_loops + 1}/{self._loops}"
                                if self._render_channels:
                                    loop_string += ", "
                            if self._render_channels:
                                loop_string += f"channel {channel_current + 1}"
                            if self._loops > 1 or self._render_channels:
                                loop_string += ")"
                            if self._render_file is not None and not self._quiet:
                                if self._verbose:
                                    rendering_string = f"Rendering: Order {mod_order_position}/{mod_song_length - 1}, Pattern {mod_order[mod_order_position]}, Line {mod_line + 1}{loop_string}   "
                                else:
                                    rendering_string = f"Rendering order {mod_order_position}/{mod_song_length - 1}{loop_string}...   "
                                print(rendering_string, end="\r")

                            for channel in range(0, mod_channels):
                                if mod_pattern_delay_finished:
                                    effect_number = mod_file[mod_pointer + 2] & 0xf  # ssssh copypasta
                                    effect_param = mod_file[mod_pointer + 3]
                                    if effect_number == 0xf:  # set tempo/ticks (checked for all channels for the note delay - fixes the weird behaviour in ode2ptk - hey, that rhymes)
                                        if effect_param < 32:
                                            self._mod_ticks = effect_param
                                        else:
                                            self._mod_tempo = effect_param
                                            mod_ms_per_tick = self._mod_get_tempo_length()
                                mod_pointer += 4
                            mod_pointer -= 4 * mod_channels

                            for channel in range(0, mod_channels):
                                # difference between mod_period and mod_raw_period:
                                # mod_period is only changed if the period is non-zero
                                # mod_raw_period is the raw period value - for example, it's used when checking if there's a sample number and no period... (this usually doesn't need to be touched)

                                mod_effect_number[channel] = mod_file[mod_pointer + 2] & 0xf
                                mod_effect_param[channel] = mod_file[mod_pointer + 3]

                                if mod_pattern_delay_finished:
                                    period = ((mod_file[mod_pointer] & 0xf) << 8) + mod_file[mod_pointer + 1]  # the period can be changed, even if there's no sample number
                                    mod_raw_period[channel] = period
                                    sample_number = (mod_file[mod_pointer] & 0xf0) + (mod_file[mod_pointer + 2] >> 4)
                                    mod_port_amount[channel] = 0
                                    mod_volslide_amount[channel] = 0
                                else:
                                    sample_number = 0
                                    mod_raw_period[channel] = 0
                                    mod_effect_number[channel] = 0
                                    mod_effect_param[channel] = 0

                                # portamento effects MUST be handled here!
                                # otherwise the periods won't be correct (the periods are updated in the code after this)
                                # that's because with the tone portamento, it uses the LAST period as the period to slide from, and then the current period is grabbed after that
                                # the normal slide up/down is still here, for consistency ;)
                                if mod_effect_number[channel] == 0x1:  # slide up
                                    mod_port_amount[channel] = mod_effect_param[channel]
                                    mod_port_fine[channel] = False
                                if mod_effect_number[channel] == 0x2:  # slide down
                                    mod_port_amount[channel] = 0 - mod_effect_param[channel]
                                    mod_port_fine[channel] = False
                                mod_tone_sliding[channel] = False
                                if (mod_effect_number[channel] == 0x3 or mod_effect_number[channel] == 0x5) and mod_tone_period[channel] > 0:
                                    mod_tone_sliding[channel] = True
                                if mod_effect_number[channel] == 0x3:
                                    if period > 0:
                                        if mod_tone_period[channel] > 0:
                                            mod_tone_sliding[channel] = True
                                        mod_tone_period[channel] = Module._mod_get_finetune_period(period, mod_finetune_temp[channel])
                                    if mod_effect_param[channel] > 0:
                                        mod_tone_memory[channel] = mod_effect_param[channel]

                                mod_retrig_counter[channel] = -1  # -1 means no retrig

                                if sample_number > 0:  # finetune check...
                                    mod_finetune_temp[channel] = mod_samples[sample_number - 1]["finetune"]

                                    mod_ticks_per_beat = self._mod_ticks * 4  # formula taken from the openmpt source code! (sndfile.cpp)
                                    mod_samples_per_beat = mod_ms_per_tick * mod_ticks_per_beat
                                    mod_bpm = (self._sample_rate / mod_samples_per_beat) * 60

                                # extended effects are here because the note delay is checked before the sample plays
                                # also the effect numbers are out of order, because that's the order i programmed them in :D
                                if mod_effect_number[channel] == 0xe:  # extended effects
                                    effect = mod_effect_param[channel] >> 4
                                    param = mod_effect_param[channel] & 0xf
                                    if effect == 0xc:  # note cut
                                        if param == 0:  # ec0 is equivalent to c00
                                            mod_sample_volume[channel] = 0
                                        else:
                                            if param >= self._mod_ticks:  # if the cut amount is the same as the ticks per line, the note plays normally
                                                mod_note_cut_ticks[channel] = -1
                                            else:
                                                mod_note_cut_ticks[channel] = param
                                    mod_note_delay_ticks[channel] = -1  # no note delay effect, reset it
                                    if effect == 0xd:  # note delay
                                        if param >= self._mod_ticks:  # if the delay amount is the same as the ticks per line, the note is ignored
                                            mod_note_delay_ticks[channel] = -2  # pro coder skillz
                                        else:
                                            mod_note_delay_ticks[channel] = param
                                    if effect == 0x6:  # pattern loop
                                        if param == 0:  # set loop start
                                            mod_pattern_loop_start[channel] = mod_line
                                        else:  # loop x amount of times
                                            mod_pattern_loop_end[channel] = mod_line
                                            if mod_pattern_loop_counter[channel] == 0:
                                                mod_pattern_loop_counter[channel] = param + 1
                                    if effect == 0xa:  # fine volume slide up
                                        mod_volslide_amount[channel] = param
                                        mod_volslide_fine[channel] = True
                                    if effect == 0xb:  # fine volume slide down
                                        mod_volslide_amount[channel] = 0 - param
                                        mod_volslide_fine[channel] = True
                                    if effect == 0x1:  # fine portamento up
                                        mod_port_amount[channel] = param
                                        mod_port_fine[channel] = True
                                    if effect == 0x2:  # fine portamento down
                                        mod_port_amount[channel] = 0 - param
                                        mod_port_fine[channel] = True
                                    if effect == 0x9:  # note retrigger
                                        mod_retrig_speed[channel] = param
                                        mod_retrig_counter[channel] = 0
                                        mod_sample_playing[channel] = True  # samples retrigger on the note... retrigger... effect.
                                        mod_sample_position[channel] = 0
                                    if effect == 0x5:  # set finetune
                                        if param > 0:
                                            mod_finetune_temp[channel] = param
                                    if effect == 0xf:  # invert loop
                                        if param == 0:
                                            mod_invert_loop_speed[channel] = 0
                                        else:
                                            mod_invert_loop_counter[channel] = 0
                                            mod_invert_loop_speed[channel] = Module._mod_funk_table[param]
                                    if effect == 0xe:  # pattern delay:
                                        mod_pattern_delay = param
                                    wave_type = param % 4
                                    wave_retrigger = (param % 8) // 4 == 0
                                    if effect == 0x4:  # vibrato wave type
                                        mod_vibrato_wave[channel] = wave_type
                                        mod_vibrato_retrigger[channel] = wave_retrigger
                                    if effect == 0x7:  # tremolo wave type
                                        mod_tremolo_wave[channel] = wave_type
                                        mod_tremolo_retrigger[channel] = wave_retrigger
                                    if effect == 0x3:  # glissando control
                                        mod_glissando[channel] = param > 0
                                    if effect == 0x0:  # filter on/off
                                        if not mod_filter_flag:
                                            mod_filter = param % 2 == 0
                                    if effect == 0x8:  # set panning
                                        if param == 15:
                                            mod_channel_pan[channel] = 1
                                        else:
                                            mod_channel_pan[channel] = ((param - 8) / 8)

                                if sample_number > 0:  # is a sample playing?
                                    mod_invert_loop_counter[channel] = 0
                                    if mod_samples[sample_number - 1]["length"] > 0:
                                        mod_sample_number[channel] = sample_number
                                    sample_number -= 1
                                    if mod_sample_number[channel] > 0 and mod_raw_period[channel] == 0:  # sample number, no period?
                                        if mod_note_delay_ticks[channel] == -1:  # if there's a note delay, the volume will be set once the counter reaches 0
                                            mod_sample_volume[channel] = mod_samples[sample_number]["volume"]
                                    else:  # sample number and period...
                                        mod_sample_offset[channel] = mod_samples[sample_number]["offset"]
                                        if not mod_tone_sliding[channel]:  # don't reset the sample position or volume if sliding notes
                                            if mod_note_delay_ticks[channel] == -1:  # this'll always be -1 unless there's a note delay effect
                                                mod_sample_playing[channel] = True
                                                mod_sample_position[channel] = 0
                                        if mod_note_delay_ticks[channel] == -1:
                                            mod_sample_volume[channel] = mod_samples[sample_number]["volume"]
                                    sample_number += 1
                                elif sample_number == 0:  # no sample number...
                                    if mod_raw_period[channel] > 0:  # period, no sample?
                                        if mod_note_delay_ticks[channel] == -1 and not mod_tone_sliding[channel]:
                                            mod_sample_playing[channel] = True
                                            mod_sample_position[channel] = 0

                                if mod_effect_number[channel] != 0x3 and period > 0:  # if there's a slide before a period, this changes it before the slide so it slides to the correct period (slideperiodslideslideperiod)
                                    mod_tone_period[channel] = Module._mod_get_finetune_period(period, mod_finetune_temp[channel])
                                if mod_tone_period[channel] == 0 and period > 0:  # nothing to slide from, use the current period
                                    mod_tone_period[channel] = period
                                if period > 0 and not mod_tone_sliding[channel] and mod_pattern_delay_finished:  # the period>0 fixes a bug related to pattern delays, if there's a period on the last channel, the period value will contain that, so without the check all channels will have the same period!
                                    mod_period[channel] = Module._mod_get_finetune_period(period, mod_finetune_temp[channel])
                                    mod_arp_period[channel] = period  # are you kidding me, that's all i had to do the entire time, i was faffing around and turns out i was trying to find the finetuned period of a finetuned period, SSCCHHHHEEEEE
                                if mod_sample_volume[channel] > 64:
                                    mod_sample_volume[channel] = 64

                                if mod_effect_number[channel] == 0x0:  # arpeggio
                                    if mod_effect_param[channel] > 0:  # 0 means ignore
                                        period_note = Module._mod_get_period_note(mod_arp_period[channel])
                                        if sample_number > 0:
                                            sample_finetune = 0

                                        if mod_effect_param[channel] >> 4 == 0:
                                            mod_arp_periods[channel][1] = Module._mod_periods[sample_finetune][period_note]
                                        else:
                                            period_1 = (period_note + (mod_effect_param[channel] >> 4)) % (mod_period_amount + 1)
                                            if period_1 > mod_period_amount - 1:
                                                mod_arp_periods[channel][1] = 0
                                            else:
                                                mod_arp_periods[channel][1] = Module._mod_periods[sample_finetune][period_1]

                                        if mod_effect_param[channel] & 0xf == 0:
                                            mod_arp_periods[channel][2] = Module._mod_periods[sample_finetune][period_note]
                                        else:
                                            period_2 = (period_note + (mod_effect_param[channel] & 0xf)) % (mod_period_amount + 1)
                                            if period_2 > mod_period_amount - 1:
                                                mod_arp_periods[channel][2] = 0
                                            else:
                                                mod_arp_periods[channel][2] = Module._mod_periods[sample_finetune][period_2]
                                        mod_arp_periods[channel][0] = Module._mod_periods[sample_finetune][period_note]
                                    else:
                                        mod_arp_periods[channel][0] = 0
                                        mod_arp_periods[channel][1] = 0
                                        mod_arp_periods[channel][2] = 0
                                        mod_arp_counter[channel] = 0
                                else:
                                    mod_arp_periods[channel][0] = 0
                                    mod_arp_periods[channel][1] = 0
                                    mod_arp_periods[channel][2] = 0
                                    mod_arp_counter[channel] = 0

                                if mod_effect_number[channel] == 0xb:  # position break
                                    mod_next_position = mod_effect_param[channel]
                                    mod_position_break = True
                                if mod_effect_number[channel] == 0xd:  # line break
                                    mod_next_line = (((mod_effect_param[channel] >> 4) * 10) + (mod_effect_param[channel] & 0xf))
                                    if mod_next_line > 64:
                                        mod_next_line = 0
                                    mod_line_break = True
                                if (mod_effect_number[channel] == 0xa or mod_effect_number[channel] == 0x5 or mod_effect_number[channel] == 0x6) and mod_pattern_delay_finished:  # volume slide/ + tone portamento/ + vibrato (volume slide doesn't have any memory)
                                    mod_volslide_fine[channel] = False
                                    if mod_effect_param[channel] >= 0x10:  # slide up
                                        mod_volslide_amount[channel] = mod_effect_param[channel] >> 4
                                    else:  # slide down
                                        mod_volslide_amount[channel] = 0 - mod_effect_param[channel]
                                if mod_effect_number[channel] == 0xc:  # set volume
                                    mod_sample_volume[channel] = mod_effect_param[channel]
                                    if mod_sample_volume[channel] > 64:
                                        mod_sample_volume[channel] = 64

                                # the offset effect has a very specific behaviour in protracker:
                                # * only change the offset if the effect is either on its own or alongside a sample number/period
                                # * only play a sample with the offset if either:
                                #     * it's a period on its own
                                #     * it's a period and a sample number alongside an offset effect
                                #     * there's no tone portamento currently happening

                                if mod_effect_number[channel] == 0x9:  # set offset
                                    if mod_effect_param[channel] > 0:
                                        mod_offset_memory[channel] = mod_effect_param[channel] * 255
                                        if mod_offset_memory[channel] > mod_samples[mod_sample_number[channel] - 1]["length"]:
                                            mod_offset_memory[channel] = mod_samples[mod_sample_number[channel] - 1]["length"]

                                if ((mod_raw_period[channel] > 0 and sample_number == 0 and mod_effect_number[channel] != 0x9) or (mod_raw_period[channel] > 0 and sample_number > 0 and mod_effect_number[channel] == 0x9) or (mod_raw_period[channel] > 0 and mod_effect_number[channel] == 0x9)) and not mod_tone_sliding[channel]:
                                    mod_sample_position[channel] = mod_offset_memory[channel]

                                mod_vibrato[channel] = False
                                mod_tremolo[channel] = False
                                if mod_effect_number[channel] == 0x4:  # vibrato
                                    memory = mod_vibrato_memory[channel]
                                elif mod_effect_number[channel] == 0x7:  # tremolo
                                    memory = mod_tremolo_memory[channel]

                                if mod_effect_number[channel] == 0x8:  # set panning
                                    if mod_effect_param[channel] == 255:
                                        mod_channel_pan[channel] = 1
                                    else:
                                        mod_channel_pan[channel] = (mod_effect_param[channel] - 128) / 128

                                if mod_raw_period[channel] > 0:  # if there's a period...
                                    if not mod_vibrato[channel]:  # ...and there's no vibrato...
                                        if mod_vibrato_retrigger[channel]:
                                            mod_vibrato_counter[channel] = 0  # ...reset the counter, otherwise the note will play slightly out of tune
                                            mod_vibrato_offset[channel] = 0
                                    if not mod_tremolo[channel]:
                                        if mod_tremolo_retrigger[channel]:
                                            mod_tremolo_counter[channel] = 0
                                            mod_tremolo_offset[channel] = 0

                                if mod_effect_number[channel] == 0x4 or mod_effect_number[channel] == 0x7:  # vibrato/tremolo
                                    if mod_effect_param[channel] > 0:
                                        if mod_effect_param[channel] >> 4 == 0:  # speed continue (4xY)
                                            memory = (memory & 0xf0) | (mod_effect_param[channel] & 0xf)
                                        elif mod_effect_param[channel] & 0xf == 0:  # depth continue (4Xy)
                                            memory = (mod_effect_param[channel] & 0xf0) | (memory & 0xf)
                                        else:  # speed and depth (4XY)
                                            memory = mod_effect_param[channel]

                                if mod_effect_number[channel] == 0x4:  # vibrato
                                    mod_vibrato_memory[channel] = memory
                                elif mod_effect_number[channel] == 0x7:  # tremolo
                                    mod_tremolo_memory[channel] = memory
                                    mod_tremolo[channel] = True

                                if mod_effect_number[channel] == 0x4 or mod_effect_number[channel] == 0x6:  # vibrato/volslide + vibrato
                                    mod_vibrato[channel] = True
                                    if mod_raw_period[channel] > 0:
                                        if mod_vibrato_retrigger[channel]:
                                            mod_vibrato_counter[channel] = 0

                                if mod_pattern_delay_finished:
                                    mod_pointer += 4  # next channel

                                if mod_arp_periods[channel] != [0, 0, 0]:
                                    for a in range(0, 3):
                                        if mod_arp_periods[channel][a] > 0:  # if the period is 0, it'll be missed entirely (in _mod_get_frequency)
                                            mod_arp_periods[channel][a] = Module._mod_get_finetune_period(mod_arp_periods[channel][a], mod_finetune_temp[channel])

                                if self._render_file is None:
                                    if self._verbose:
                                        note_name = "---"
                                        note_number = Module._mod_get_period_note(mod_raw_period[channel])
                                        if note_number >= 0:
                                            note_name = mod_note_names[note_number]
                                        sample_number_string = str(sample_number).zfill(2)
                                        effect_string = hex(mod_effect_number[channel])[2:].upper() + " " + hex(mod_effect_param[channel])[2:].upper().zfill(2)
                                        line_string += f"{note_name} {sample_number_string} {effect_string}|"

                            # channels finished

                            if self._render_file is None:
                                if self._verbose:
                                    order_position_string = str(mod_order_position).zfill(3) + "/" + str(mod_song_length - 1).zfill(3)
                                    pattern_string = str(mod_order[mod_order_position]).zfill(3)
                                    line_number_string = str(mod_line).zfill(2)
                                    if not self._quiet:
                                        print(f"O{order_position_string}, P{pattern_string}, L{line_number_string}:|{line_string}")
                                else:
                                    if not self._quiet:
                                        if self._loops > 1:
                                            loops_string = f", Loop: {mod_loops + 1}/{self._loops}"
                                        else:
                                            loops_string = ""
                                        print(f"Time elapsed: {time_elapsed_string}, Tempo: {self._mod_tempo}, Ticks/Line: {self._mod_ticks}, BPM: {'%g' % mod_bpm}, Order {mod_order_position}/{mod_song_length - 1}, Pattern {mod_order[mod_order_position]}, Line {(mod_line + 1)}{loops_string}        ", end="\r")

                            mod_ticks_counter = 0
                            mod_ticks_counter_actual = 0  # the actual tick counter (e.g. by default this'll be from 0-6)
                            mod_ticks_counter_actual_previous = 0

                            while mod_ticks_counter < mod_ms_per_tick * self._mod_ticks:
                                channel_sum_last = (channel_sum + 32768) & 65535
                                channel_sum_left_last = (channel_sum_left + 32768) & 65535
                                channel_sum_right_last = (channel_sum_right + 32768) & 65535
                                mod_ticks_counter_actual_previous = mod_ticks_counter_actual
                                mod_ticks_counter_actual = int((mod_ticks_counter / (mod_ms_per_tick * self._mod_ticks)) * self._mod_ticks)
                                for channel in range(0, mod_channels):
                                    if mod_ticks_counter_actual_previous != mod_ticks_counter_actual or mod_ticks_counter == 0:  # on every tick (including the first)
                                        fine_condition = mod_ticks_counter_actual > 0
                                        if mod_volslide_fine[channel]:
                                            fine_condition = mod_ticks_counter_actual == 0  # only fineslide on the first tick
                                        if fine_condition:
                                            if mod_volslide_amount[channel] >= 0:
                                                mod_sample_volume[channel] += mod_volslide_amount[channel]
                                                if mod_sample_volume[channel] > 65:
                                                    mod_sample_volume[channel] = 65
                                            else:
                                                mod_sample_volume[channel] += mod_volslide_amount[channel]
                                                if mod_sample_volume[channel] < 0:
                                                    mod_sample_volume[channel] = 0

                                        fine_condition = mod_ticks_counter_actual > 0
                                        if mod_port_fine[channel]:
                                            fine_condition = mod_ticks_counter == 0  # only fineslide on the first tick
                                        if mod_port_amount[channel] != 0 and fine_condition:  # portamento happening?
                                            mod_period[channel] -= mod_port_amount[channel]
                                        if mod_tone_sliding[channel] and mod_ticks_counter_actual > 0:  # don't slide on the first tick
                                            if mod_period[channel] < mod_tone_period[channel] - mod_tone_memory[channel]:  # first note higher than second note?
                                                mod_period[channel] += mod_tone_memory[channel]
                                            elif mod_period[channel] > mod_tone_period[channel] + mod_tone_memory[channel]:  # second note higher than first note?
                                                mod_period[channel] -= mod_tone_memory[channel]
                                            else:
                                                mod_period[channel] = mod_tone_period[channel]

                                        if mod_period[channel] > 0:
                                            if mod_glissando[channel]:
                                                mod_frequency[channel] = Module._mod_get_frequency(Module._mod_get_closest_period(mod_period[channel], mod_samples[sample_number]["finetune"]))
                                            else:
                                                if mod_arp_periods[channel] != [0, 0, 0]:
                                                    if mod_arp_periods[channel][mod_arp_counter[channel]] > 0:
                                                        mod_frequency[channel] = Module._mod_get_frequency(mod_arp_periods[channel][mod_arp_counter[channel]])
                                                    else:
                                                        mod_frequency[channel] = 0
                                                else:
                                                    mod_frequency[channel] = Module._mod_get_frequency(mod_period[channel] + mod_vibrato_offset[channel])
                                        if mod_arp_periods[channel] != [0, 0, 0]:
                                            if self._mod_ticks == 2:
                                                mod_arp_counter[channel] += 2
                                            elif self._mod_ticks > 2:
                                                mod_arp_counter[channel] += 1
                                            if mod_arp_counter[channel] > 2:
                                                mod_arp_counter[channel] = 0

                                    sample_number = mod_sample_number[channel]
                                    if sample_number > 0:
                                        sample_number -= 1
                                        if mod_samples[sample_number]["loop_length"] <= 2:  # sample isn't looping
                                            if mod_sample_position[channel] > mod_samples[sample_number]["length"] - 1:  # reached end of sample?
                                                mod_sample_playing[channel] = False  # not looping, end sample
                                        else:  # sample is looping
                                            if mod_sample_position[channel] > (mod_samples[sample_number]["loop_length"] + mod_samples[sample_number]["loop_start"]):  # reached loop point?
                                                mod_sample_position[channel] -= mod_samples[sample_number]["loop_length"]  # loop back
                                                # it's not possible to simply set the position to the loop start, because the sample stepping accuracy will be lost, especially with higher notes

                                    if mod_ticks_counter_actual_previous != mod_ticks_counter_actual:  # a tick has occured
                                        # because of the condition above, the first tick will be missed entirely, which is the correct behaviour
                                        if mod_invert_loop_speed[channel] > 0:
                                            mod_invert_loop_counter[channel] += mod_invert_loop_speed[channel]
                                            if mod_invert_loop_counter[channel] > 127:
                                                mod_invert_loop_counter[channel] = 0
                                                mod_invert_loop_position[channel] += 1
                                                if mod_invert_loop_position[channel] > mod_samples[sample_number]["loop_length"] + mod_samples[sample_number]["loop_start"] - 1:
                                                    mod_invert_loop_position[channel] = 0
                                                sample_unsigned = (mod_file[mod_samples[sample_number]["offset"] + mod_invert_loop_position[channel]] + 128) & 255  # convert the sample byte to unsigned
                                                sample_unsigned = ~sample_unsigned & 255  # find the bitwise not of the byte
                                                sample_unsigned = (sample_unsigned + 128) & 255  # convert it back to signed
                                                mod_file[mod_samples[sample_number]["offset"] + mod_invert_loop_position[channel]] = sample_unsigned
                                        if mod_retrig_counter[channel] >= 0:
                                            mod_retrig_counter[channel] += 1
                                            if mod_retrig_counter[channel] == mod_retrig_speed[channel]:
                                                mod_sample_playing[channel] = True
                                                mod_sample_position[channel] = 0
                                                mod_retrig_counter[channel] = 0

                                        if mod_vibrato[channel] or mod_tremolo[channel]:
                                            if mod_vibrato[channel]:
                                                counter = mod_vibrato_counter[channel]
                                                memory = mod_vibrato_memory[channel]
                                                wave_type = mod_vibrato_wave[channel]
                                            else:
                                                counter = mod_tremolo_counter[channel]
                                                memory = mod_tremolo_memory[channel]
                                                wave_type = mod_tremolo_wave[channel]
                                            depth = memory & 0xf
                                            if wave_type == 0:  # sine
                                                offset = (Module._mod_sine_table[counter] * depth) / 128
                                            elif wave_type == 1:  # ramp down
                                                offset = ((counter - 32) * 8 * depth) / 128
                                            elif wave_type == 2:  # square
                                                offset = depth * 255
                                                if counter > 31:
                                                    offset = 0 - offset
                                                offset /= 128
                                            elif wave_type == 3:  # random
                                                offset = random.randint(0 - depth, depth)

                                            if mod_vibrato[channel]:
                                                mod_vibrato_offset[channel] = offset
                                                mod_vibrato_counter[channel] += memory >> 4
                                                mod_vibrato_counter[channel] = mod_vibrato_counter[channel] % len(Module._mod_sine_table)
                                            else:
                                                mod_tremolo_offset[channel] = offset
                                                mod_tremolo_counter[channel] += memory >> 4
                                                mod_tremolo_counter[channel] = mod_tremolo_counter[channel] % len(Module._mod_sine_table)

                                        if mod_note_cut_ticks[channel] >= 0:  # note actually cutting?
                                            mod_note_cut_ticks[channel] -= 1
                                            if mod_note_cut_ticks[channel] == 0:
                                                mod_note_cut_ticks[channel] = -1
                                                mod_sample_volume[channel] = 0
                                        # despite the name, the note cut doesn't actually cut at all, it just changes the volume to 0
                                        # if you put a sample number on the same line as a note cut, the volume will open up before being cut by the effect
                                        if mod_note_delay_ticks[channel] >= 0:  # note delayed?
                                            mod_note_delay_ticks[channel] -= 1
                                            if mod_note_delay_ticks[channel] == 0:
                                                mod_note_delay_ticks[channel] = -1
                                                mod_sample_playing[channel] = True
                                                mod_sample_position[channel] = 0
                                                mod_sample_volume[channel] = mod_samples[sample_number]["volume"]
                                        elif mod_note_delay_ticks[channel] == -2:  # previously specified delay command greater than the ticks per line?
                                            mod_note_delay_ticks[channel] = -1  # the note didn't play, so reset tick counter
                                            # this works because there are explicit checks to only play the note if the tick counter has reached -1!!

                                    sample_step_rate = mod_frequency[channel] / self._sample_rate

                                    if mod_sample_playing[channel] and (self._render_file is None or not self._render_channels or channel == channel_current):
                                        sample_byte_position = int(mod_sample_offset[channel] + mod_sample_position[channel])
                                        if sample_byte_position > len(mod_file) - 1:
                                            sample_byte_position = len(mod_file) - 1
                                        sample_byte = (((mod_file[sample_byte_position] + 128) & 255) - 128) / 128
                                        volume = mod_sample_volume[channel] + mod_tremolo_offset[channel]
                                        if volume > 64:
                                            volume = 64
                                        if volume < 0:
                                            volume = 0
                                        volume /= 64
                                        sample_byte *= volume
                                        sample_byte = int((sample_byte * 32768) + 32768)
                                        mod_sample_position[channel] += sample_step_rate
                                    else:
                                        sample_byte = 32768
                                        if sample_byte_last != 32768:
                                            sample_byte_last = 32768

                                    mod_channel_byte[channel] = sample_byte

                                channel_sum = 0
                                channel_sum_left = 0
                                channel_sum_right = 0
                                for counter, channel_byte in enumerate(mod_channel_byte):
                                    if stereo:
                                        channel_byte_panned = Module._get_panned_bytes(channel_byte, mod_channel_pan[counter])
                                        channel_sum_left += int(channel_byte_panned[0] * 2) + 32768
                                        channel_sum_right += int(channel_byte_panned[1] * 2) + 32768

                                    else:
                                        channel_sum += channel_byte

                                if stereo:
                                    channel_sum_left //= mod_channels_adjusted
                                    channel_sum_right //= mod_channels_adjusted
                                    if channel_sum_left > 65535:
                                        channel_sum_left = 65535
                                    if channel_sum_left < 0:
                                        channel_sum_left = 0
                                    if channel_sum_right > 65535:
                                        channel_sum_right = 65535
                                    if channel_sum_right < 0:
                                        channel_sum_right = 0
                                else:
                                    channel_sum //= mod_channels_adjusted

                                if mod_filter:
                                    if stereo:
                                        channel_sum_left = (channel_sum_left + channel_sum_left_last) // 2
                                        channel_sum_right = (channel_sum_right + channel_sum_right_last) // 2
                                    else:
                                        channel_sum = (channel_sum + channel_sum_last) // 2

                                if stereo:
                                    channel_sum_left = (channel_sum_left + 32768) & 65535
                                    channel_sum_right = (channel_sum_right + 32768) & 65535
                                    channel_sum_stereo = channel_sum_left | (channel_sum_right << 16)
                                else:
                                    channel_sum = (channel_sum + 32768) & 65535

                                if self._render_file is not None:  # if rendering a file, append sample bytes to the finished file
                                    if stereo:
                                        file_finished.append(channel_sum_left & 255)
                                        file_finished.append(channel_sum_left >> 8)
                                        file_finished.append(channel_sum_right & 255)
                                        file_finished.append(channel_sum_right >> 8)
                                    else:
                                        file_finished.append(channel_sum & 255)
                                        file_finished.append(channel_sum >> 8)
                                else:  # if not rendering, write to stream
                                    if stereo:
                                        stream.write(channel_sum_stereo.to_bytes(length=4, byteorder="little"))
                                    else:
                                        stream.write(channel_sum.to_bytes(length=2, byteorder="little"))

                                mod_ticks_counter += 1

                            mod_looped = False  # it only makes sense to add one loop at a time... this also fixes some duplicate loop errors
                            if mod_pattern_delay == 0:
                                if mod_position_break:
                                    if not mod_line_break:  # position break on its own?
                                        mod_next_line = 0  # if so, reset to beginning of pattern
                                        if mod_next_position == mod_order_position:  # if a position breaks to itself without a line break, that counts as a loop
                                            mod_loops += 1
                                            mod_looped = True
                                    mod_pointer = mod_pattern_offsets[mod_order[mod_next_position]] + (mod_next_line * 4 * mod_channels)
                                    mod_order_position = mod_next_position  # change current order
                                    mod_line = 0  # reset line COUNTER
                                else:
                                    mod_line += 1

                                # there's one pattern loop per channel!!
                                any_pattern_loops = False
                                for channel in range(0, mod_channels):
                                    if mod_pattern_loop_start[channel] >= 0:
                                        if mod_pattern_loop_counter[channel] > 0 and mod_line - 1 == mod_pattern_loop_end[channel]:
                                            mod_line = mod_pattern_loop_start[channel]
                                            mod_pointer = mod_pattern_offsets[mod_order[mod_order_position]] + (mod_line * 4 * mod_channels)
                                            mod_pattern_loop_counter[channel] -= 1
                                            if mod_pattern_loop_counter[channel] == 0:
                                                mod_pattern_loop_start[channel] = -1
                                                mod_line = mod_pattern_loop_end[channel] + 1
                                                mod_pattern_loop_end[channel] = -1
                                                mod_pointer = mod_pattern_offsets[mod_order[mod_order_position]] + (mod_line * 4 * mod_channels)
                                    if mod_pattern_loop_counter[channel] > 0:
                                        any_pattern_loops = True

                                if mod_line_break:
                                    if not mod_position_break:
                                        mod_order_position += 1
                                        if mod_order_position > mod_song_length - 1:
                                            mod_order_position = 0
                                            if not mod_looped:
                                                mod_looped = True
                                                mod_loops += 1
                                    mod_line = mod_next_line
                                    mod_pointer = mod_pattern_offsets[mod_order[mod_order_position]] + (mod_next_line * 4 * mod_channels)

                                if (mod_position_break or mod_line_break) and not any_pattern_loops:
                                    if [mod_order_position, mod_line] in mod_jumps:  # has this specific line and order been visited before?
                                        if not mod_looped:
                                            mod_looped = True
                                            mod_loops += 1
                                        mod_jumps.clear()
                                    else:
                                        if mod_order_position in mod_orders_visited:  # has this order been visited before? (used for position jumps determining the loop point)
                                            if not mod_looped:
                                                mod_looped = True
                                                mod_loops += 1
                                            mod_orders_visited.clear()
                                        mod_jumps.append([mod_order_position, mod_line])

                                mod_position_break = False
                                mod_line_break = False

                                if mod_loops > self._loops - 1:
                                    mod_order_position = mod_song_length  # end
                                    mod_line = mod_lines

                            if mod_pattern_delay > 0:
                                mod_pattern_delay_finished = False
                                mod_pattern_delay -= 1
                            else:
                                mod_pattern_delay_finished = True

                        mod_orders_visited.append(mod_order_position)
                        if not mod_line_break:  # position breaks reset the line anyway
                            mod_line = 0
                        if mod_song_length > 1:
                            mod_order_position += 1
                            if mod_order_position == mod_song_length:
                                mod_order_position = 0
                                mod_pointer = mod_pattern_offsets[mod_order[0]]
                                mod_line = 0
                                if not mod_looped:
                                    mod_looped = True
                                    mod_loops += 1
                        else:
                            if not mod_looped:
                                mod_looped = True
                                mod_loops += 1
                        if mod_loops > self._loops - 1:  # copypasta SSSSHHHHH (but this is for when the pattern ends, not per line... so if you're line breaking/position breaking this won't be reached)
                            mod_order_position = mod_song_length  # end
                            mod_line = mod_lines
                        mod_pointer = mod_pattern_offsets[mod_order[mod_order_position]]

                    if not while_condition or (self._render_file is not None and self._render_channels):
                        file_name = self._render_file if not self._render_channels else ".".join(self._render_file.split(".")[:-1])[:-2] + "_" + str(channel_current + 1) + "." + self._render_file.split(".")[-1]
                        with wave.open(file_name, "wb") as wave_file:
                            if stereo:
                                wave_file.setnchannels(2)
                            else:
                                wave_file.setnchannels(1)
                            wave_file.setsampwidth(2)
                            wave_file.setframerate(self._sample_rate)
                            wave_file.writeframesraw(bytearray(file_finished))
                        file_finished.clear()
                        channel_current += 1

                if self._render_file is not None:
                    end_time = time.perf_counter() - start_time
                    minutes = int(end_time // 60)  # for some reason it was giving me 1.0 even though it's integer division :/
                    seconds = int(end_time % 60)
                    if not self._quiet:
                        print()
                        stringy = "Rendered in "
                        if minutes == 0:
                            stringy += f"{seconds} seconds!"
                        elif minutes == 1:
                            stringy += f"1 minute, {seconds} seconds!"
                        else:
                            stringy += f"{minutes} minutes, {seconds} seconds!"
                        print(stringy)
                else:
                    if not self._quiet:
                        print()
                        print("Done!")
                    stream.stop_stream()
                    stream.close()
                    pya.terminate()

    def set_sample_rate(self, rate):
        self._sample_rate = rate

    def set_nb_of_loops(self, nb_of_loops):
        self._loops = nb_of_loops

    def set_play_mode(self, play_mode):
        self._play_mode = play_mode

    def set_verbose(self, flag):
        self._verbose = flag

    def set_buffer_size(self, size):
        self._buffer_size = size

    def set_quiet(self, flag):
        self._quiet = flag

    def play(self):
        self._run()

    def render_to(self, filepath, separate_channels=False):
        self._render_file = filepath
        self._render_channels = separate_channels
        self._run()
