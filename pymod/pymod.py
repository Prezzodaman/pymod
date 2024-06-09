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


# -- Classes
class Module:
    """Python class that plays/renders ProTracker modules using PyAudio."""

    # -- Class Variables

    # extended periods nabbed from a taketracker module :D
    # 2 extra octaves, one below the lowest note, and one above the highest note!
    _mod_extended_periods = [
        # no finetune
        [
            1712, 1616, 1524, 1440, 1356, 1280, 1208, 1140, 1076, 1016, 960, 906,
            856, 808, 762, 720, 678, 640, 604, 570, 538, 508, 480, 453,
            428, 404, 381, 360, 339, 320, 302, 285, 269, 254, 240, 226,
            214, 202, 190, 180, 170, 160, 151, 143, 135, 127, 120, 113,
            107, 101, 95, 90, 85, 80, 76, 72, 68, 64, 60, 56, 0
        ],
        [  # finetune +1
            1700, 1604, 1514, 1430, 1348, 1274, 1202, 1134, 1070, 1010, 954, 900,
            850, 802, 757, 715, 674, 637, 601, 567, 535, 505, 477, 450,
            425, 401, 379, 357, 337, 318, 300, 284, 268, 253, 239, 225,
            213, 201, 189, 179, 169, 159, 150, 142, 134, 126, 119, 113,
            106, 100, 94, 89, 84, 79, 75, 71, 67, 63, 59, 56, 0
        ],
        [  # +2
            1688, 1592, 1504, 1418, 1340, 1264, 1194, 1126, 1064, 1004, 948, 894,
            844, 796, 752, 709, 670, 632, 597, 563, 532, 502, 474, 447,
            422, 398, 376, 355, 335, 316, 298, 282, 266, 251, 237, 224,
            211, 199, 188, 177, 167, 158, 149, 141, 133, 125, 118, 112,
            105, 99, 93, 88, 83, 78, 74, 70, 66, 62, 59, 56, 0
        ],
        [  # +3
            1676, 1582, 1492, 1408, 1330, 1256, 1184, 1118, 1056, 996, 940, 888,
            838, 791, 746, 704, 665, 628, 592, 559, 528, 498, 470, 444,
            419, 395, 373, 352, 332, 314, 296, 280, 264, 249, 235, 222,
            209, 198, 187, 176, 166, 157, 148, 140, 132, 125, 118, 111,
            104, 99, 93, 88, 83, 78, 74, 70, 66, 62, 59, 56, 0
        ],
        [  # +4
            1664, 1570, 1482, 1398, 1320, 1246, 1176, 1110, 1048, 990, 934, 882,
            832, 785, 741, 699, 660, 623, 588, 555, 524, 495, 467, 441,
            416, 392, 370, 350, 330, 312, 294, 278, 262, 247, 233, 220,
            208, 196, 185, 175, 165, 156, 147, 139, 131, 124, 117, 110,
            104, 98, 92, 87, 82, 77, 73, 69, 65, 62, 58, 56, 0
        ],
        [  # +5
            1652, 1558, 1472, 1388, 1310, 1238, 1168, 1102, 1040, 982, 926, 874,
            826, 779, 736, 694, 655, 619, 584, 551, 520, 491, 463, 437,
            413, 390, 368, 347, 328, 309, 292, 276, 260, 245, 232, 219,
            206, 195, 184, 174, 164, 155, 146, 138, 130, 123, 116, 109,
            103, 97, 92, 87, 82, 77, 73, 69, 65, 61, 58, 56, 0
        ],
        [  # +6
            1640, 1548, 1460, 1378, 1302, 1228, 1160, 1094, 1032, 974, 920, 868,
            820, 774, 730, 689, 651, 614, 580, 547, 516, 487, 460, 434,
            410, 387, 365, 345, 325, 307, 290, 274, 258, 244, 230, 217,
            205, 193, 183, 172, 163, 154, 145, 137, 129, 122, 115, 109,
            102, 96, 91, 86, 81, 77, 72, 68, 64, 61, 57, 56, 0
        ],
        [  # +7
            1628, 1536, 1450, 1368, 1292, 1220, 1150, 1086, 1026, 968, 914, 862,
            814, 768, 725, 684, 646, 610, 575, 543, 513, 484, 457, 431,
            407, 384, 363, 342, 323, 305, 288, 272, 256, 242, 228, 216,
            204, 192, 181, 171, 161, 152, 144, 136, 128, 121, 114, 108,
            102, 96, 90, 85, 80, 76, 72, 68, 64, 60, 57, 56, 0
        ],
        [  # -8
            1814, 1712, 1616, 1524, 1440, 1356, 1280, 1208, 1140, 1076, 1016, 960,
            907, 856, 808, 762, 720, 678, 640, 604, 570, 538, 508, 480,
            453, 428, 404, 381, 360, 339, 320, 302, 285, 269, 254, 240,
            226, 214, 202, 190, 180, 170, 160, 151, 143, 135, 127, 120,
            113, 107, 101, 95, 90, 85, 80, 75, 71, 67, 63, 60, 0
        ],
        [  # -7
            1800, 1700, 1604, 1514, 1430, 1350, 1272, 1202, 1134, 1070, 1010, 954,
            900, 850, 802, 757, 715, 675, 636, 601, 567, 535, 505, 477,
            450, 425, 401, 379, 357, 337, 318, 300, 284, 268, 253, 238,
            225, 212, 200, 189, 179, 169, 159, 150, 142, 134, 126, 119,
            112, 106, 100, 94, 89, 84, 79, 75, 71, 67, 63, 59, 0
        ],
        [  # -6
            1788, 1688, 1592, 1504, 1418, 1340, 1264, 1194, 1126, 1064, 1004, 948,
            894, 844, 796, 752, 709, 670, 632, 597, 563, 532, 502, 474,
            447, 422, 398, 376, 355, 335, 316, 298, 282, 266, 251, 237,
            223, 211, 199, 188, 177, 167, 158, 149, 141, 133, 125, 118,
            111, 105, 99, 94, 88, 83, 79, 74, 70, 66, 62, 59, 0
        ],
        [  # -5
            1774, 1676, 1582, 1492, 1408, 1330, 1256, 1184, 1118, 1056, 996, 940,
            887, 838, 791, 746, 704, 665, 628, 592, 559, 528, 498, 470,
            444, 419, 395, 373, 352, 332, 314, 296, 280, 264, 249, 235,
            222, 209, 198, 187, 176, 166, 157, 148, 140, 132, 125, 118,
            111, 104, 99, 93, 88, 83, 78, 74, 70, 66, 62, 59, 0
        ],
        [  # -4
            1762, 1664, 1570, 1482, 1398, 1320, 1246, 1176, 1110, 1048, 988, 934,
            881, 832, 785, 741, 699, 660, 623, 588, 555, 524, 494, 467,
            441, 416, 392, 370, 350, 330, 312, 294, 278, 262, 247, 233,
            220, 208, 196, 185, 175, 165, 156, 147, 139, 131, 123, 117,
            110, 104, 98, 92, 87, 82, 78, 73, 69, 65, 61, 58, 0
        ],
        [  # -3
            1750, 1652, 1558, 1472, 1388, 1310, 1238, 1168, 1102, 1040, 982, 926,
            875, 826, 779, 736, 694, 655, 619, 584, 551, 520, 491, 463,
            437, 413, 390, 368, 347, 328, 309, 292, 276, 260, 245, 232,
            219, 206, 195, 184, 174, 164, 155, 146, 138, 130, 123, 116,
            109, 103, 97, 92, 86, 82, 77, 73, 69, 65, 61, 58, 0
        ],
        [  # -2
            1736, 1640, 1548, 1460, 1378, 1302, 1228, 1160, 1094, 1032, 974, 920,
            868, 820, 774, 730, 689, 651, 614, 580, 547, 516, 487, 460,
            434, 410, 387, 365, 345, 325, 307, 290, 274, 258, 244, 230,
            217, 205, 193, 183, 172, 163, 154, 145, 137, 129, 122, 115,
            108, 102, 96, 91, 86, 81, 77, 72, 68, 64, 61, 57, 0
        ],
        [  # -1
            1724, 1628, 1536, 1450, 1368, 1292, 1220, 1150, 1086, 1026, 968, 914,
            862, 814, 768, 725, 684, 646, 610, 575, 543, 513, 484, 457,
            431, 407, 384, 363, 342, 323, 305, 288, 272, 256, 242, 228,
            216, 203, 192, 181, 171, 161, 152, 144, 136, 128, 121, 114,
            108, 101, 96, 90, 85, 80, 76, 72, 68, 64, 60, 58, 0
        ]
    ]

    _mod_legacy_periods = [
        [  # no finetune
            856, 808, 762, 720, 678, 640, 604, 570, 538, 508, 480, 453,
            428, 404, 381, 360, 339, 320, 302, 285, 269, 254, 240, 226,
            214, 202, 190, 180, 170, 160, 151, 143, 135, 127, 120, 113
        ],
        [  # finetune +1
            850, 802, 757, 715, 674, 637, 601, 567, 535, 505, 477, 450,
            425, 401, 379, 357, 337, 318, 300, 284, 268, 253, 239, 225,
            213, 201, 189, 179, 169, 159, 150, 142, 134, 126, 119, 113
        ],
        [  # +2
            844, 796, 752, 709, 670, 632, 597, 563, 532, 502, 474, 447,
            422, 398, 376, 355, 335, 316, 298, 282, 266, 251, 237, 224,
            211, 199, 188, 177, 167, 158, 149, 141, 133, 125, 118, 112
        ],
        [  # +3
            838, 791, 746, 704, 665, 628, 592, 559, 528, 498, 470, 444,
            419, 395, 373, 352, 332, 314, 296, 280, 264, 249, 235, 222,
            209, 198, 187, 176, 166, 157, 148, 140, 132, 125, 118, 111
        ],
        [  # +4
            832, 785, 741, 699, 660, 623, 588, 555, 524, 495, 467, 441,
            416, 392, 370, 350, 330, 312, 294, 278, 262, 247, 233, 220,
            208, 196, 185, 175, 165, 156, 147, 139, 131, 124, 117, 110
        ],
        [  # +5
            826, 779, 736, 694, 655, 619, 584, 551, 520, 491, 463, 437,
            413, 390, 368, 347, 328, 309, 292, 276, 260, 245, 232, 219,
            206, 195, 184, 174, 164, 155, 146, 138, 130, 123, 116, 109
        ],
        [  # +6
            820, 774, 730, 689, 651, 614, 580, 547, 516, 487, 460, 434,
            410, 387, 365, 345, 325, 307, 290, 274, 258, 244, 230, 217,
            205, 193, 183, 172, 163, 154, 145, 137, 129, 122, 115, 109
        ],
        [  # +7
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

    _mod_arp_period_cap = _mod_legacy_periods[0][-1]  # the highest note (lowest period) of the default finetune
    _mod_legacy_period_lowest = _mod_legacy_periods[0][-1]  # these aren't TECHNICALLY the highest and lowest... but according to protracker, they are
    _mod_legacy_period_highest = _mod_legacy_periods[0][0]

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
    def _generateTestFiles(cls, keep_old_wavs=False):
        """Generate all the test files used to compare against in the unit tests.
           This should only be used in a local repo and not with an installed module."""

        source_folder = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
        modules_folder = os.path.join(source_folder, "tests", "modules")
        wavs_folder = os.path.join(source_folder, "tests", "wavs")
        if keep_old_wavs:
            os.rename(wavs_folder, os.path.join(source_folder, "tests", "wavs_old"))
            os.mkdir(wavs_folder)

        if not os.path.exists(modules_folder) or not os.path.exists(wavs_folder):
            print("Error: This should be used on a local repo, not an installed module.")
            return

        test_modules = os.listdir(modules_folder)
        for number, filename in enumerate(test_modules):
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
            print(f"{number + 1}/{len(test_modules)}: Rendering {base_name}...")
            module.render_to(os.path.join(wavs_folder, os.path.splitext(filename)[0] + ".wav"))

    @classmethod
    def _mod_get_frequency(cls, period):
        if period > 0:
            return 7093789 / (period * 2)
        else:
            return 0

    @classmethod
    def _mod_get_period_note(cls, period, legacy):  # returns the note value
        note = -1
        found = False
        if legacy:
            if period < Module._mod_legacy_period_lowest:
                period = Module._mod_legacy_period_lowest
            elif period > Module._mod_legacy_period_highest:
                period = Module._mod_legacy_period_highest
            for period_set in Module._mod_legacy_periods:
                if period in period_set and not found:
                    note = period_set.index(period)
                    found = True
        else:
            for period_set in Module._mod_extended_periods:
                if period in period_set and not found:
                    note = period_set.index(period)
                    found = True
                if period + 1 in period_set and not found:  # i need to find a better way of doing this :D
                    note = period_set.index(period + 1)
                    found = True
                if period - 1 in period_set and not found:
                    note = period_set.index(period - 1)
                    found = True
        return note

    @classmethod
    def _mod_get_finetune_period(cls, period, finetune, legacy):
        if legacy:
            period_found = Module._mod_legacy_periods[finetune][Module._mod_get_period_note(period, legacy)]
            if period_found < Module._mod_arp_period_cap:
                period_found = Module._mod_arp_period_cap
        else:
            period_found = Module._mod_extended_periods[finetune][Module._mod_get_period_note(period, legacy)]
        return period_found

    @classmethod
    def _mod_get_closest_period(cls, period, finetune, legacy):
        differences = []
        if legacy:
            for period_2 in Module._mod_legacy_periods[finetune]:
                differences.append(abs(period - period_2))
            return Module._mod_legacy_periods[finetune][differences.index(min(differences))]
        else:
            for period_2 in Module._mod_extended_periods[finetune]:
                differences.append(abs(period - period_2))
            return Module._mod_extended_periods[finetune][differences.index(min(differences))]

    @classmethod
    def _get_panned_bytes(cls, byte, pan):  # expects (and returns) a signed byte between -32768 and 32767. pan value is between -1 and 1 (left and right)
        return int(byte * ((pan / 2) - 0.5)), 0 - int((byte * ((pan / 2) + 0.5)))

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

    @classmethod
    def sample_rate_default(cls):
        return 44100

    # -- Instance Methods
    def __init__(self, input_file_path, sample_rate=0, play_mode="mono", verbose=False, quiet=False, legacy=False, amplify=1, interpolate=False):
        """Constructor based on command line arguments."""

        # these are set based on the keyword arguments, when initializing a Module object
        if sample_rate == 0:  # there's got to be a better way
            self._sample_rate = Module.sample_rate_default()
        else:
            self._sample_rate = sample_rate
        self._input_file = input_file_path
        self._play_mode = play_mode
        self._verbose = verbose
        self._quiet = quiet  # this only affects the program's "introduction", playback and rendering - showing module info will still work
        self._legacy = legacy
        self._amplify = amplify
        self._interpolate = interpolate

        # these are just defaults
        self._render_file = None
        self._loops_init = 1
        self._render_channels = False
        self._buffer_size = Module.buffer_size_default()
        self._mod_tempo = 125
        self._mod_ticks = 6

    # https://modarchive.org/forums/index.php?topic=2709.0
    def _mod_get_tempo_length(self):
        return (2500 / self._mod_tempo) * (self._sample_rate / 1000)

    def _run(self):
        self._mod_tempo = 125
        self._mod_ticks = 6
        self._loops = self._loops_init

        if not self._quiet:
            print(f"Pymod v{__version__}")
            print("by Presley Peters, 2023-present")
            print()

        with open(self._input_file, "rb") as file:
            mod_file = bytearray(file.read())  # we're converting to a bytearray so the "invert loop" effect works (byte objects are immutable)

        sample_rate_minimum = 1000
        sample_rate_temp = self._sample_rate
        self._sample_rate = sample_rate_minimum  # using an extremely low sample rate for the estimation since it's WAY quicker, and gives basically the same result when you times it up (it's accurate enough for percentages and time estimates, so there's that!)
        mod_ms_per_tick = self._mod_get_tempo_length()
        mod_ticks_counter = 0

        mod_channels = 0
        mod_type = ""
        for a in range(1080, 1084):
            mod_type += chr(mod_file[a])
        if mod_type == "M.K.":
            mod_channels = 4
            mod_type_string = "ProTracker / Generic module tracker"
        elif mod_type == "M!K!":
            mod_channels = 4
            mod_type_string = "ProTracker / Generic module tracker (65 or more patterns)"
        elif mod_type.endswith("CHN"):
            try:
                mod_channels = int(mod_type[:1])
                mod_type_string = "Generic module tracker"
            except Exception:  # not an integer...
                pass  # ...mod_channels will remain 0, and the appropriate error will be returned
        elif mod_type.endswith("CH"):
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

        if mod_channels == 0:
            print("Error: Invalid module!")
            if self._render_file is not None:
                os.remove(self._render_file)
        elif self._sample_rate < sample_rate_minimum or self._sample_rate > 380000:
            print(f"Error: Sample rate must be between {sample_rate_minimum} and 380000!")
            if self._render_file is not None:
                os.remove(self._render_file)
        elif self._play_mode not in Module.play_modes():
            play_modes_string = ", ".join(Module.play_modes())
            print(f"Error: Invalid play mode: {self._play_mode}. Accepted modes: {play_modes_string}")
            if self._render_file is not None:
                os.remove(self._render_file)
        elif self._buffer_size < 0 or self._buffer_size > 8192:
            print("Error: Buffer size must be between 0 and 8192!")
            if self._render_file is not None:
                os.remove(self._render_file)
        elif self._render_file is not None and self._render_channels and not self._render_file.endswith("_1.wav"):
            print("Error: File name is suffixed incorrectly for channel rendering!")
            os.remove(self._render_file)
        elif self._render_file is not None and os.path.splitext(self._render_file)[-1].lower() != ".wav":
            print("Error: Output must be a .wav file!")
            if self._render_file is not None:
                os.remove(self._render_file)
        elif self._render_file is None and self._render_channels:
            print("Error: The --channels/-c option can only be used alongside the --render/-r option!")
        elif self._legacy and (mod_type != "M.K." and mod_type != "M!K!"):
            print("Error: Only 4 channel modules can be used in legacy mode!")
            if self._render_file is not None:
                os.remove(self._render_file)
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

            sample = {"name": "", "length": 4, "finetune": 0, "volume": 0, "loop_start": 0, "loop_length": 4, "offset": 0}  # an empty sample, used for loop swapping
            mod_samples.append(sample)

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

            if self._play_mode == "text":
                print("Module text:")
                print()
                for sample in range(0, mod_samples_amount):
                    print(mod_samples[sample]["name"])
            else:
                estimate = True
                mod_note_names = []
                mod_note_letters = ["C-", "C#", "D-", "D#", "E-", "F-", "F#", "G-", "G#", "A-", "A#", "B-"]
                if self._legacy:
                    for a in range(0, len(Module._mod_legacy_periods[0])):
                        mod_note_names.append(mod_note_letters[a % len(mod_note_letters)] + str((a // 12) + 4))
                else:
                    for a in range(0, len(Module._mod_extended_periods[0])):
                        mod_note_names.append(mod_note_letters[a % len(mod_note_letters)] + str((a // 12) + 3))

                file_finished = []

                if self._render_file is None and self._play_mode != "info":
                    pya = pyaudio.PyAudio()
                    channels = 1
                    if stereo:
                        channels += 1
                    stream = pya.open(format=pyaudio.paInt16, rate=sample_rate_temp, output=True, channels=channels, frames_per_buffer=self._buffer_size)

                if self._render_file is None and not self._verbose and not self._quiet and not self._play_mode == "info" and not estimate:
                    print("Playing...")

                channel_sum = 0
                channel_sum_left = 0
                channel_sum_right = 0
                channel_current = 0  # used when rendering individual channels
                while_condition = True
                mod_using_bass_channel = False  # optimize playback by skipping the dsp for effects that aren't used in the module
                mod_using_delay_channel = False
                mod_overall_length = 0  # for some reason this is VERY slightly off (even when all the conditions are true... no clue why), but it's Close Enough(tm)
                mod_bytes_rendered = 0
                if estimate:
                    estimating_length = True
                    if not self._quiet:
                        print("Estimating length...", end="\r")
                else:
                    estimating_length = False
                    estimate = False
                    start_time = time.perf_counter()
                estimated_length = 0
                estimated_length_minutes = 0
                estimated_length_seconds = 0

                if self._play_mode == "info":
                    if not estimate:
                        while_condition = False
                    self._loops = 1
                while while_condition:
                    mod_jumps = [[0, 0]]
                    mod_orders_visited = []
                    mod_lines_visited = []

                    # these are here, because when rendering channels, they need to be reset every time
                    mod_filter = self._play_mode.endswith("filter")  # a <crude> "simulation" of the amiga hardware filter (it's a simple one pole low-pass filter - literally just finding the difference between the current and last byte)
                    mod_filter_flag = mod_filter  # unlike mod_filter, this can't be changed
                    if self._legacy:
                        mod_period_amount = len(Module._mod_legacy_periods[0])
                    else:
                        mod_period_amount = len(Module._mod_extended_periods[0])

                    mod_channel_byte = [0] * mod_channels  # the current byte in each channel, summed together later on
                    mod_filter_order_base = 64  # the desired order at 44100hz (trying to keep the value somewhat low so it renders/plays faster. for the standard filter, only the first byte of mod_channel_byte_last is used)
                    mod_filter_order = int((mod_filter_order_base / 44100) * self._sample_rate)
                    mod_delay_length_base = 2000  # the desired delay length at 44100hz
                    mod_delay_length = int((mod_delay_length_base / 44100) * self._sample_rate)
                    mod_delay_counter = 0
                    mod_channel_delay_buffer = []
                    mod_channel_byte_last_temp = []
                    mod_channel_delay_buffer_temp = []
                    for a in range(0, mod_filter_order):
                        mod_channel_byte_last_temp.append(0)
                    for a in range(0, mod_delay_length):
                        mod_channel_delay_buffer_temp.append(0)
                    mod_channel_byte_last = []
                    mod_channel_pan = [0] * mod_channels  # -1 = left, 0 = centre, 1 = right
                    for a in range(0, mod_channels):
                        mod_channel_byte_last.append(mod_channel_byte_last_temp.copy())
                        mod_channel_delay_buffer.append(mod_channel_delay_buffer_temp.copy())
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
                    mod_sample_number = [0] * mod_channels  # actually contains the number of the currently playing sample, even if none is specified!
                    mod_sample_playing = [False] * mod_channels
                    mod_sample_volume = [0] * mod_channels

                    mod_period = [0] * mod_channels
                    mod_next_period = [0] * mod_channels  # used for protracker's note delay behaviour with looped samples (this will contain the actual current period, but it won't play it until the note delay is reached)
                    mod_raw_period = [0] * mod_channels
                    mod_raw_period_inc_delay = [0] * mod_channels  # raw period + pattern delay (so when a pattern is being delayed, there's still a period number in this variable... mod_raw_period would contain 0 in this case)
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
                    mod_invert_loop_counter = [0] * mod_channels  # 0  =  no inversion
                    mod_invert_loop_position = [0] * mod_channels
                    mod_invert_loop_speed = [0] * mod_channels
                    mod_finetune_temp = [0] * mod_channels  # for the "set finetune" effect, which doesn't directly affect the sample. if there's no effect, this'll contain the default finetune, otherwise, it'll be overridden. this is used when finding the frequency based on the period values, so it's actually very important!
                    mod_glissando = [False] * mod_channels
                    mod_bass_channel = [False] * mod_channels  # pymod exclusive feature: use the effect e02 on a channel with bass sounds on it (e.g. bass drums or sub basses) to remove the ringing :D (e03 turns the bass filter off)
                    mod_delay_channel = [False] * mod_channels  # pymod exclusive feature: use the effect e04 or e05 on a channel to add a crude reverb simulation! (e06 turns it off)
                    mod_sample_reversed = [False] * mod_channels  # pymod exclusive feature: use the effect e07 to play a sample in reverse (or e08 to play it forwards again)
                    mod_sample_reversed_flag = [False] * mod_channels
                    mod_delay_channel_fast = [False] * mod_channels
                    mod_loop_play_full = [False] * mod_channels  # if this is false, the sample's loop will play as expected. if the sample is looping but the loop starts at 0, this will be true, meaning the whole sample will have to play through before looping
                    mod_sample_number_cued = [0] * mod_channels  # the next sample to be played once a loop's finished, if another sample number is specified (if a sample is just being played normally from the start, this should match mod_sample_number!)
                    mod_offset_flag = [False] * mod_channels
                    mod_offset_delay_flag = [False] * mod_channels

                    mod_tone_memory = [0] * mod_channels
                    mod_offset_memory = [0] * mod_channels
                    mod_vibrato_memory = [0] * mod_channels
                    mod_tremolo_memory = [0] * mod_channels

                    mod_pattern_loop_start = [-1] * mod_channels  # -1 if there's no loop right now
                    mod_pattern_loop_end = [-1] * mod_channels
                    mod_pattern_loop_counter = [0] * mod_channels  # counts down on every loop
                    mod_pattern_delay = 0  # if 0, there's no delay. if above 0, it counts down. the pattern only plays if this is 0 and mod_pattern_delay_finished is true
                    mod_pattern_delay_finished = True  # if this is false, it waits until the next line to stop advancing the mod pointer (without this flag, it would hang on whatever channel the effect was encountered on)
                    mod_pattern_delay_encountered = False  # is there a pattern delay effect on the current line?

                    mod_next_position = 0
                    mod_next_line = 0
                    mod_next_line_offset = False  # in protracker, using a pattern delay alongside a line break adds 1 to the line... for some reason
                    mod_position_break = False
                    mod_line_break = False

                    mod_order_position = 0
                    mod_pointer = mod_pattern_offsets[mod_order[mod_order_position]]
                    mod_line = 0
                    mod_loops = 0  # different to the "loops" variable, this increases until it reaches "loops"
                    mod_bpm = 0  # calculated from the tempo and ticks/line (only used for a visual indicator)

                    sample_byte = 0

                    if estimating_length:
                        while_condition = True
                    else:
                        if self._render_channels:
                            while_condition = channel_current < mod_channels - 1
                        else:
                            while_condition = False
                    while mod_order_position < mod_song_length:
                        while mod_line < mod_lines:
                            if not self._quiet:
                                if estimate and not estimating_length:
                                    percent_rendered = (mod_bytes_rendered / (mod_overall_length * (self._sample_rate / sample_rate_minimum)))
                                    if self._render_channels:
                                        percent_rendered /= mod_channels
                                    percent_rendered = int(percent_rendered * 100)
                                    percentage_string = f" ({percent_rendered}%)"
                                else:
                                    percentage_string = ""
                                if not estimating_length:
                                    current_time = time.perf_counter()
                                    time_elapsed = int(current_time - start_time)
                                    time_elapsed_minutes = time_elapsed // 60
                                    time_elapsed_seconds = time_elapsed % 60
                                    time_elapsed_string = f"{time_elapsed_minutes}m {time_elapsed_seconds}s".ljust(6, " ")
                                    if estimate:
                                        time_remaining = int(estimated_length) - time_elapsed
                                        if time_remaining < 0:  # man, that accuracy
                                            time_remaining = 0
                                        time_remaining_minutes = time_remaining // 60
                                        time_remaining_seconds = time_remaining % 60
                                        time_elapsed_string += "(-" + f"{time_remaining_minutes}m {time_remaining_seconds}s".rjust(6, " ") + ")"

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
                            if self._render_file is not None and not self._quiet and not estimating_length:
                                if self._verbose:
                                    rendering_string = f"Rendering{percentage_string}: Order {mod_order_position}/{mod_song_length - 1}, Pattern {mod_order[mod_order_position]}, Line {mod_line + 1}{loop_string}   "
                                else:
                                    rendering_string = f"Rendering order {mod_order_position}/{mod_song_length - 1}{loop_string}{percentage_string}...   "
                                print(rendering_string, end="\r")

                            mod_pattern_delay_encountered = False
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
                                    if effect_number == 0xe and effect_param >> 4 == 0xe and self._legacy:  # pattern delay and line breaks (should this be part of legacy mode?)
                                        mod_next_line_offset = True
                                        mod_pattern_delay_encountered = True
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
                                    mod_raw_period_inc_delay[channel] = period
                                    sample_number = (mod_file[mod_pointer] & 0xf0) + (mod_file[mod_pointer + 2] >> 4)
                                    mod_port_amount[channel] = 0
                                    mod_volslide_amount[channel] = 0
                                else:
                                    sample_number = 0
                                    mod_raw_period[channel] = 0
                                    mod_effect_number[channel] = 0
                                    mod_effect_param[channel] = 0

                                if not estimating_length:
                                    # portamento effects MUST be handled here!
                                    # otherwise the periods won't be correct (the periods are updated in the code after this)
                                    # that's because with the tone portamento, it uses the LAST period as the period to slide from, and then the current period is grabbed after that
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
                                            mod_tone_period[channel] = Module._mod_get_finetune_period(period, mod_finetune_temp[channel], self._legacy)
                                        if mod_effect_param[channel] > 0:
                                            mod_tone_memory[channel] = mod_effect_param[channel]

                                    if mod_pattern_delay_finished:
                                        mod_retrig_speed[channel] = 0

                                    if sample_number > 0:  # finetune check...
                                        mod_finetune_temp[channel] = mod_samples[sample_number - 1]["finetune"]

                                if sample_number > 0:
                                    mod_ticks_per_beat = self._mod_ticks * 4  # formula taken from the openmpt source code! (sndfile.cpp)
                                    mod_samples_per_beat = mod_ms_per_tick * mod_ticks_per_beat
                                    mod_bpm = (self._sample_rate / mod_samples_per_beat) * 60

                                # extended effects are here because the note delay is checked before the sample plays
                                if mod_effect_number[channel] == 0xe:  # extended effects
                                    effect = mod_effect_param[channel] >> 4
                                    param = mod_effect_param[channel] & 0xf
                                    if not estimating_length:  # skipping as many irrelevant effects as possible when estimating the length!!
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
                                            if param > 0:
                                                mod_retrig_speed[channel] = param
                                                mod_sample_playing[channel] = True
                                                mod_sample_position[channel] = 0
                                        if effect == 0x5:  # set finetune
                                            mod_finetune_temp[channel] = param
                                        if effect == 0xf:  # invert loop
                                            if param == 0:
                                                mod_invert_loop_speed[channel] = 0
                                            else:
                                                mod_invert_loop_counter[channel] = 0
                                                mod_invert_loop_speed[channel] = Module._mod_funk_table[param]
                                        wave_type = param % 4
                                        wave_retrigger = param % 8 < 4
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
                                                if self._legacy or (not self._legacy and param < 2):
                                                    mod_filter = param % 2 == 0
                                        if effect == 0x8:  # set panning
                                            if not self._legacy:  # this effect isn't supported in protracker 2.3!
                                                if param == 15:
                                                    mod_channel_pan[channel] = 1
                                                else:
                                                    mod_channel_pan[channel] = ((param - 8) / 8)

                                    if effect == 0x6:  # pattern loop
                                        if param == 0:  # set loop start
                                            mod_pattern_loop_start[channel] = mod_line
                                        else:  # loop x amount of times
                                            mod_pattern_loop_end[channel] = mod_line
                                            if mod_pattern_loop_counter[channel] == 0:
                                                mod_pattern_loop_counter[channel] = param + 1
                                    if effect == 0xe:  # pattern delay:
                                        mod_pattern_delay = param

                                    mod_sample_reversed_flag[channel] = False
                                    if effect == 0x0 and not self._legacy:  # pymod exclusive effects
                                        if param == 2:  # bass channel filter on
                                            mod_bass_channel[channel] = True
                                            mod_using_bass_channel = True
                                        elif param == 3:  # bass channel filter off
                                            mod_bass_channel[channel] = False
                                        if param == 4:  # channel delay on (fast decay)
                                            mod_delay_channel[channel] = True
                                            mod_delay_channel_fast[channel] = True
                                            mod_using_delay_channel = True
                                        if param == 5:  # channel delay on (slow decay)
                                            mod_delay_channel[channel] = True
                                            mod_delay_channel_fast[channel] = False
                                            mod_using_delay_channel = True
                                        elif param == 6:  # channel delay off
                                            mod_delay_channel[channel] = False
                                        elif param == 7:  # sample reverse
                                            mod_sample_reversed[channel] = True
                                            mod_sample_reversed_flag[channel] = period > 0
                                        elif param == 8:  # sample forwards
                                            mod_sample_reversed[channel] = False

                                if not estimating_length:
                                    if sample_number > 0:  # is a sample playing?
                                        mod_invert_loop_counter[channel] = 0
                                        if mod_samples[sample_number - 1]["length"] == 0 and mod_pattern_delay_finished:  # is the current sample empty?
                                            sample_number = 32  # play an empty "sample"
                                        mod_sample_number_cued[channel] = sample_number  # "cue up" the next sample
                                        if mod_samples[sample_number - 1]["loop_start"] == 0 and mod_samples[sample_number - 1]["loop_length"] > 2:  # is this sample looping and does the loop start at 0?
                                            if not mod_sample_playing[channel]:  # is there no sample currently playing?
                                                mod_loop_play_full[channel] = True  # the full sample must be played first
                                        else:  # not looping
                                            if not mod_sample_playing[channel]:
                                                mod_loop_play_full[channel] = False  # idk if this is correct, half of the loop code is guess work and playing it by ear
                                        if mod_sample_position[channel] == 0:  # sample hasn't played yet?
                                            mod_sample_number[channel] = sample_number  # ...play it
                                        # if the sample is empty, none of that code will be executed, so nothing will be played
                                        sample_number -= 1
                                        if mod_sample_number[channel] > 0 and mod_raw_period[channel] == 0:  # sample number, no period?
                                            if mod_note_delay_ticks[channel] == -1 and sample_number != 31:  # if there's a note delay, the volume will be set once the counter reaches 0
                                                mod_sample_volume[channel] = mod_samples[sample_number]["volume"]
                                        elif mod_sample_number[channel] > 0 and mod_raw_period[channel] > 0:  # sample number and period...
                                            mod_sample_offset[channel] = mod_samples[sample_number]["offset"]
                                            if not mod_tone_sliding[channel]:  # don't reset the sample position or volume if sliding notes
                                                if mod_note_delay_ticks[channel] == -1 or (mod_note_delay_ticks[channel] > 0 and mod_samples[sample_number]["loop_length"] > 2 and self._legacy):  # this'll always be -1 unless there's a note delay effect
                                                    mod_sample_playing[channel] = True
                                                    if mod_sample_reversed_flag[channel]:  # has a "reverse" effect been encountered?
                                                        mod_sample_position[channel] = mod_samples[mod_sample_number[channel] - 1]["length"] - 1
                                                    else:  # no reverse effect, play sample normally
                                                        mod_sample_position[channel] = 0
                                                        mod_sample_reversed[channel] = False
                                            if mod_note_delay_ticks[channel] == -1 or (mod_note_delay_ticks[channel] > 0 and mod_samples[sample_number]["loop_length"] > 2 and self._legacy):
                                                mod_sample_volume[channel] = mod_samples[sample_number]["volume"]
                                        sample_number += 1
                                    elif sample_number == 0:  # no sample number...
                                        if mod_raw_period[channel] > 0:  # period, no sample?
                                            if mod_note_delay_ticks[channel] == -1 and not mod_tone_sliding[channel]:
                                                mod_sample_playing[channel] = True
                                                if mod_sample_reversed_flag[channel]:  # has a "reverse" effect been encountered?
                                                    mod_sample_position[channel] = mod_samples[mod_sample_number[channel] - 1]["length"] - 1
                                                else:  # no reverse effect, play sample normally
                                                    mod_sample_position[channel] = 0
                                                    mod_sample_reversed[channel] = False
                                    if mod_raw_period[channel] > 0:  # period, regardless of sample number?
                                        if mod_samples[mod_sample_number_cued[channel] - 1]["loop_start"] == 0:  # i seriously have no clue if this is correct
                                            mod_loop_play_full[channel] = True  # a period will reset this flag
                                        if mod_sample_number[channel] != mod_sample_number_cued[channel]:
                                            mod_sample_offset[channel] = mod_samples[mod_sample_number_cued[channel] - 1]["offset"]
                                            if mod_sample_reversed_flag[channel]:  # has a "reverse" effect been encountered?
                                                mod_sample_position[channel] = mod_samples[mod_sample_number_cued[channel] - 1]["length"] - 1
                                            else:  # no reverse effect, play sample normally
                                                mod_sample_position[channel] = 0
                                                mod_sample_reversed[channel] = False
                                        mod_sample_number[channel] = mod_sample_number_cued[channel]

                                    if mod_effect_number[channel] != 0x3 and period > 0:  # if there's a slide before a period, this changes it before the slide so it slides to the correct period (slideperiodslideslideperiod)
                                        # that comment continues to crack me up
                                        mod_tone_period[channel] = Module._mod_get_finetune_period(period, mod_finetune_temp[channel], self._legacy)
                                    if mod_tone_period[channel] == 0 and period > 0:  # nothing to slide from, use the current period
                                        mod_tone_period[channel] = period
                                    if period > 0 and not mod_tone_sliding[channel] and mod_pattern_delay_finished:  # the period>0 fixes a bug related to pattern delays, if there's a period on the last channel, the period value will contain that, so without the check all channels will have the same period!
                                        mod_period_temp = Module._mod_get_finetune_period(period, mod_finetune_temp[channel], self._legacy)
                                        if mod_note_delay_ticks[channel] == -1:
                                            mod_period[channel] = mod_period_temp
                                        else:
                                            mod_next_period[channel] = mod_period_temp
                                        mod_arp_period[channel] = period  # are you kidding me, that's all i had to do the entire time, i was faffing around and turns out i was trying to find the finetuned period of a finetuned period, SSCCHHHHEEEEE
                                    if mod_sample_volume[channel] > 64:
                                        mod_sample_volume[channel] = 64

                                    if mod_effect_number[channel] == 0x0:  # arpeggio
                                        if mod_effect_param[channel] > 0:  # 0 means ignore
                                            mod_arp_counter[channel] = 0  # reset the counter every time the effect is encountered
                                            period_note = Module._mod_get_period_note(mod_arp_period[channel], self._legacy)
                                            sample_finetune_temp = sample_finetune
                                            sample_finetune_temp_changed = False  # so the finetune isn't repeatedly increased

                                            if mod_effect_param[channel] >> 4 == 0:
                                                if self._legacy:
                                                    mod_arp_periods[channel][1] = Module._mod_legacy_periods[sample_finetune][period_note]
                                                else:
                                                    mod_arp_periods[channel][1] = Module._mod_extended_periods[sample_finetune][period_note]
                                            else:
                                                period_1 = period_note + (mod_effect_param[channel] >> 4)  # this actually contains the note number, not the period... ;) (the reason it's the period amount+1 is because there's like this extra "period" containing no note when arpeggiating, causing a "cutting" effect)
                                                if period_1 == mod_period_amount:
                                                    mod_arp_periods[channel][1] = 0  # don't play the note at all
                                                else:
                                                    if period_1 > mod_period_amount:
                                                        sample_finetune_temp = (sample_finetune_temp + 1) % len(Module._mod_legacy_periods)  # when a wraparound occurs, the finetune is increased by one, because on the amiga, the period table is stored as one long list, so it reaches the lowest note of the finetune next to the one used with the current sample!
                                                        sample_finetune_temp_changed = True
                                                        period_1 -= mod_period_amount
                                                    if self._legacy:
                                                        mod_arp_periods[channel][1] = Module._mod_legacy_periods[sample_finetune_temp][period_1]
                                                    else:
                                                        mod_arp_periods[channel][1] = Module._mod_extended_periods[sample_finetune_temp][period_1]

                                            if mod_effect_param[channel] & 0xf == 0:
                                                if self._legacy:
                                                    mod_arp_periods[channel][2] = Module._mod_legacy_periods[sample_finetune][period_note]  # still using the regular finetune for this, since the wraparound hasn't occured
                                                else:
                                                    mod_arp_periods[channel][2] = Module._mod_extended_periods[sample_finetune][period_note]
                                            else:
                                                period_2 = period_note + (mod_effect_param[channel] & 0xf)
                                                if period_2 == mod_period_amount:
                                                    mod_arp_periods[channel][2] = 0
                                                else:
                                                    if period_2 > mod_period_amount:
                                                        if not sample_finetune_temp_changed:
                                                            sample_finetune_temp = (sample_finetune_temp + 1) % len(Module._mod_legacy_periods)  # no need to set the flag here since it's the last of the 2 periods!
                                                        period_2 -= mod_period_amount
                                                    if self._legacy:
                                                        mod_arp_periods[channel][2] = Module._mod_legacy_periods[sample_finetune_temp][period_2]
                                                    else:
                                                        mod_arp_periods[channel][2] = Module._mod_extended_periods[sample_finetune_temp][period_2]
                                            if self._legacy:
                                                mod_arp_periods[channel][0] = Module._mod_legacy_periods[sample_finetune][period_note]
                                            else:
                                                mod_arp_periods[channel][0] = Module._mod_extended_periods[sample_finetune][period_note]
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
                                    if mod_next_line_offset and mod_pattern_delay_encountered:  # this ensures the line addition only happens if the line break is ALONGSIDE a pattern delay
                                        mod_next_line_offset = False
                                        mod_next_line += 1
                                        if mod_next_line > 63:
                                            mod_next_line = 0
                                            mod_order_position += 1
                                        mod_orders_visited.append(mod_order_position)
                                    mod_line_break = True

                                if not estimating_length:
                                    if mod_effect_number[channel] == 0x8:  # set panning
                                        if not self._legacy:  # this effect isn't supported in protracker 2.3!
                                            if mod_effect_param[channel] == 255:
                                                mod_channel_pan[channel] = 1
                                            else:
                                                mod_channel_pan[channel] = (mod_effect_param[channel] - 128) / 128

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

                                    mod_offset_delay_flag[channel] = False
                                    if mod_effect_number[channel] == 0x9:  # set offset
                                        if mod_effect_param[channel] > 0:
                                            mod_offset_memory[channel] = (mod_effect_param[channel] * 255) + 255
                                            if mod_offset_memory[channel] > mod_samples[mod_sample_number[channel] - 1]["length"]:
                                                mod_offset_memory[channel] = mod_samples[mod_sample_number[channel] - 1]["length"]

                                    if mod_raw_period[channel] > 0 and sample_number > 0 and mod_effect_number[channel] != 0x9:
                                        mod_offset_flag[channel] = False
                                    elif (mod_raw_period[channel] == 0 and sample_number > 0 and mod_effect_number[channel] == 0x9) or (mod_raw_period[channel] > 0 and sample_number > 0 and mod_effect_number[channel] == 0x9):
                                        mod_offset_flag[channel] = True
                                    if ((mod_raw_period[channel] > 0 and sample_number == 0 and mod_effect_number[channel] != 0x9) or (mod_raw_period[channel] > 0 and sample_number > 0 and mod_effect_number[channel] == 0x9) or (mod_raw_period[channel] > 0 and mod_effect_number[channel] == 0x9)) and not mod_tone_sliding[channel]:
                                        if mod_offset_flag[channel]:
                                            if mod_note_delay_ticks[channel] == -1:
                                                mod_sample_position[channel] = mod_offset_memory[channel]
                                            else:
                                                mod_offset_delay_flag[channel] = True

                                    # vibrato/tremolo

                                    mod_vibrato[channel] = False
                                    mod_tremolo[channel] = False
                                    if mod_effect_number[channel] == 0x4:  # vibrato
                                        memory = mod_vibrato_memory[channel]
                                    elif mod_effect_number[channel] == 0x7:  # tremolo
                                        memory = mod_tremolo_memory[channel]

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

                                    if mod_arp_periods[channel] != [0, 0, 0]:
                                        for a in range(0, 3):
                                            if mod_arp_periods[channel][a] > 0:  # if the period is 0, it'll be missed entirely (in _mod_get_frequency)
                                                mod_arp_periods[channel][a] = Module._mod_get_finetune_period(mod_arp_periods[channel][a], mod_finetune_temp[channel], self._legacy)

                                    if self._render_file is None:
                                        if self._verbose:
                                            note_name = "---"
                                            note_number = Module._mod_get_period_note(mod_raw_period[channel], self._legacy)
                                            if self._legacy:
                                                if note_number >= 0 and note_number < mod_period_amount - 1:
                                                    note_name = mod_note_names[note_number]
                                            else:
                                                if note_number < mod_period_amount - 1:
                                                    note_name = mod_note_names[note_number]
                                            sample_number_string = str(sample_number).zfill(2)
                                            effect_string = hex(mod_effect_number[channel])[2:].upper() + " " + hex(mod_effect_param[channel])[2:].upper().zfill(2)
                                            line_string += f"{note_name} {sample_number_string} {effect_string}|"
                                if mod_pattern_delay_finished:
                                    mod_pointer += 4  # next channel

                            # channels finished

                            if self._render_file is None and not estimating_length:
                                if self._verbose:
                                    if self._loops > 1:
                                        line_string += f" ({mod_loops+1}/{self._loops})"
                                    order_position_string = str(mod_order_position).zfill(3) + "/" + str(mod_song_length - 1).zfill(3)
                                    pattern_string = str(mod_order[mod_order_position]).zfill(3)
                                    line_number_string = str(mod_line).zfill(2)
                                    if not self._quiet:
                                        print(f"O{order_position_string}, P{pattern_string}, L{line_number_string}:|{line_string} {time_elapsed_string}")
                                else:
                                    if not self._quiet:
                                        if self._loops > 1:
                                            loops_string = f", Loop: {mod_loops + 1}/{self._loops}"
                                        else:
                                            loops_string = ""
                                        print(f"Time elapsed: {time_elapsed_string}, Tempo: {self._mod_tempo}, Ticks/Line: {self._mod_ticks}, BPM: {'%g' % mod_bpm}, Order {mod_order_position}/{mod_song_length - 1}, Pattern {mod_order[mod_order_position]}, Line {(mod_line + 1)}{loops_string}        ", end="\r")

                            mod_ticks_counter = 0
                            mod_ticks_counter_actual = 0  # the actual tick counter (e.g. by default this'll be from 0-5)
                            mod_ticks_counter_actual_previous = 0

                            while mod_ticks_counter < mod_ms_per_tick * self._mod_ticks:
                                mod_ticks_counter_actual_previous = mod_ticks_counter_actual
                                mod_ticks_counter_actual = int((mod_ticks_counter / (mod_ms_per_tick * self._mod_ticks)) * self._mod_ticks)
                                if not estimating_length:
                                    for channel in range(0, mod_channels):
                                        if mod_using_bass_channel:
                                            mod_channel_byte_last[channel].insert(0, mod_channel_byte[channel])  # stores a "byte history" of sorts, inserting the last byte at the beginning, shifting the others over to the right
                                            mod_channel_byte_last[channel].pop()  # remove the last element after insertion, keeping the list the same size
                                        else:  # only the last byte is required for the filter "simulation"
                                            mod_channel_byte_last[channel] = [mod_channel_byte[channel]]

                                        if mod_ticks_counter_actual_previous != mod_ticks_counter_actual or mod_ticks_counter == 0:  # on every tick (including the first)
                                            if mod_retrig_speed[channel] > 0:
                                                if mod_ticks_counter_actual % mod_retrig_speed[channel] == 0:
                                                    if mod_raw_period_inc_delay[channel] > 0 and self._legacy:  # note alongside the retrigger?
                                                        if mod_ticks_counter_actual > 0:  # miss the second occurence of the first tick
                                                            mod_sample_playing[channel] = True
                                                            mod_sample_position[channel] = 0
                                                    else:  # retrigger by itself?
                                                        mod_sample_playing[channel] = True  # retrigger on all ticks
                                                        mod_sample_position[channel] = 0
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

                                            if self._legacy:
                                                if mod_period[channel] < Module._mod_legacy_period_lowest:
                                                    mod_period[channel] = Module._mod_legacy_period_lowest
                                                if mod_period[channel] > Module._mod_legacy_period_highest:
                                                    mod_period[channel] = Module._mod_legacy_period_highest
                                            if mod_period[channel] > 0:
                                                if mod_glissando[channel]:
                                                    mod_frequency[channel] = Module._mod_get_frequency(Module._mod_get_closest_period(mod_period[channel], mod_samples[sample_number]["finetune"], self._legacy))
                                                else:
                                                    if mod_arp_periods[channel] == [0, 0, 0]:  # no arpeggio?
                                                        if self._legacy and mod_ticks_counter_actual == 0:  # reset to base note on the first tick
                                                            mod_frequency[channel] = Module._mod_get_frequency(mod_period[channel])
                                                        else:
                                                            mod_frequency[channel] = Module._mod_get_frequency(mod_period[channel] + mod_vibrato_offset[channel])
                                                    else:
                                                        if mod_arp_periods[channel][mod_arp_counter[channel]] > 0:
                                                            mod_frequency[channel] = Module._mod_get_frequency(mod_arp_periods[channel][mod_arp_counter[channel]])
                                                        else:
                                                            mod_frequency[channel] = 0
                                            if mod_arp_periods[channel] != [0, 0, 0]:
                                                mod_arp_counter[channel] += 1
                                                if mod_arp_counter[channel] > 2:
                                                    mod_arp_counter[channel] = 0

                                        sample_number = mod_sample_number[channel]
                                        if sample_number > 0:
                                            sample_number -= 1
                                            if mod_samples[sample_number]["loop_length"] <= 2:  # sample isn't looping
                                                if mod_sample_position[channel] > mod_samples[sample_number]["length"] - 1 or mod_sample_position[channel] < 0:  # reached end of sample?
                                                    mod_sample_playing[channel] = False  # not looping, end sample
                                            else:  # sample is looping
                                                if mod_loop_play_full[channel]:  # the current sample's loop begins at 0, play the whole thing first
                                                    if mod_sample_position[channel] > mod_samples[sample_number]["length"]:  # reached end?
                                                        mod_loop_play_full[channel] = False  # sample has played in full
                                                        if mod_samples[mod_sample_number_cued[channel] - 1]["loop_length"] <= 2:  # is the cued sample looping?
                                                            mod_sample_playing[channel] = False  # if not, stop playback
                                                        mod_sample_number[channel] = mod_sample_number_cued[channel]  # idk if this is technically correct
                                                        mod_sample_offset[channel] = mod_samples[mod_sample_number_cued[channel] - 1]["offset"]
                                                        mod_sample_position[channel] = mod_samples[mod_sample_number_cued[channel] - 1]["loop_start"]
                                                else:  # sample has either played in full, or the loop begins after 0
                                                    if mod_sample_position[channel] > mod_samples[sample_number]["loop_length"] + mod_samples[sample_number]["loop_start"]:  # reached loop point?
                                                        mod_sample_position[channel] -= mod_samples[sample_number]["loop_length"]  # loop back
                                                        # it's not possible to simply set the position to the loop start, because the sample stepping accuracy will be lost, especially with higher notes
                                                        if mod_sample_number[channel] != mod_sample_number_cued[channel]:  # reached the loop end... is the currently looping sample number different to the cued one?
                                                            if mod_samples[mod_sample_number_cued[channel] - 1]["loop_length"] > 2:  # is the cued sample looping?
                                                                if mod_sample_number_cued[channel] == 32:
                                                                    mod_sample_number[channel] = mod_sample_number_cued[channel]
                                                                    mod_sample_volume[channel] = 0
                                                                else:
                                                                    mod_sample_number[channel] = mod_sample_number_cued[channel]
                                                                    mod_sample_offset[channel] = mod_samples[mod_sample_number_cued[channel] - 1]["offset"]
                                                                    mod_sample_position[channel] = mod_samples[mod_sample_number_cued[channel] - 1]["loop_start"]
                                                            else:  # cued sample isn't looping, so stop playback altogether
                                                                mod_sample_playing[channel] = False
                                                                mod_sample_number[channel] = mod_sample_number_cued[channel]

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
                                                if wave_type == 1:  # ramp down
                                                    offset = ((counter - 32) * 8 * depth) / 128
                                                # the random waveform isn't implemented in protracker 2.3, square is used instead
                                                if wave_type == 2 or (wave_type == 3 and self._legacy):  # square
                                                    offset = depth * 255
                                                    if counter > 31:
                                                        offset = 0 - offset
                                                    offset /= 128
                                                if wave_type == 3 and not self._legacy:  # random
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
                                                if mod_note_delay_ticks[channel] == 0:  # note delay finished?
                                                    mod_note_delay_ticks[channel] = -1
                                                    if mod_samples[sample_number]["loop_length"] > 2:  # sample looping?
                                                        mod_period[channel] = mod_next_period[channel]  # just change the period without restarting the sample
                                                        mod_frequency[channel] = Module._mod_get_frequency(mod_period[channel])
                                                    else:
                                                        if mod_offset_delay_flag[channel]:
                                                            mod_sample_position[channel] = mod_offset_memory[channel]
                                                        else:
                                                            mod_sample_position[channel] = 0  # sample isn't looping, so start it from the beginning
                                                    mod_sample_playing[channel] = True  # spent over an hour trying to figure out why this didn't work... turns out THIS LINE was in the wrong place... SSSSSSCCCCCCHHHHSSSSHHHHH
                                                    mod_sample_volume[channel] = mod_samples[sample_number]["volume"]
                                            elif mod_note_delay_ticks[channel] == -2:  # previously specified delay command greater than the ticks per line?
                                                mod_note_delay_ticks[channel] = -1  # the note didn't play, so reset tick counter
                                                # this works because there are explicit checks to only play the note if the tick counter has reached -1!!

                                        sample_step_rate = mod_frequency[channel] / self._sample_rate

                                        if mod_sample_playing[channel] and (self._render_file is None or not self._render_channels or channel == channel_current):
                                            sample_byte_position = int(mod_sample_offset[channel] + mod_sample_position[channel])
                                            if sample_byte_position > len(mod_file) - 1:
                                                sample_byte_position = len(mod_file) - 1
                                            sample_byte = (mod_file[sample_byte_position] + 128) & 255  # sample byte converted to an unsigned value
                                            if self._interpolate:
                                                # source: none, i stayed up until half 2 coding this "algorithm" in bed ;)
                                                sample_position_mod = mod_sample_position[channel] % 1  # current position between 0.0 and 0.9 recurring
                                                if sample_byte_position + 1 > len(mod_file) - 1:
                                                    sample_byte_next = sample_byte
                                                else:
                                                    sample_byte_next = (mod_file[sample_byte_position + 1] + 128) & 255
                                                sample_byte <<= 8  # convert to 16-bit to remove noise!
                                                sample_byte_next <<= 8
                                                sample_byte_difference = sample_byte_next - sample_byte  # the difference between the current and next bytes
                                                sample_byte_step = sample_byte_difference * sample_position_mod  # how much to add/subtract depending on the current position
                                                sample_byte_16 = ((mod_file[sample_byte_position] + 128) & 255) << 8  # the CURRENT sample byte, converted to an unsigned 16 bit value...
                                                sample_byte_interpolated = sample_byte_16 + sample_byte_step  # apply the step difference
                                                sample_byte = (sample_byte_interpolated - 32768) / 32768  # convert to a value between -1 and 1
                                            else:
                                                sample_byte = (sample_byte - 128) / 128  # convert to a value between -1 and 1
                                            if self._legacy and mod_ticks_counter_actual == 0:  # reset to base volume on the first tick
                                                volume = mod_sample_volume[channel]
                                            else:
                                                volume = mod_sample_volume[channel] + mod_tremolo_offset[channel]
                                            if volume > 64:
                                                volume = 64
                                            if volume < 0:
                                                volume = 0
                                            volume /= 64
                                            volume *= self._amplify
                                            sample_byte *= volume
                                            sample_byte /= mod_channels  # it makes way more sense to reduce the volume per-channel instead of overall
                                            sample_byte = int(sample_byte * 32768)
                                            if mod_sample_reversed[channel]:
                                                mod_sample_position[channel] -= sample_step_rate
                                            else:
                                                mod_sample_position[channel] += sample_step_rate
                                        else:
                                            sample_byte = 0

                                        mod_channel_byte[channel] = sample_byte

                                    channel_sum = 0
                                    channel_sum_left = 0
                                    channel_sum_right = 0
                                    for counter, channel_byte in enumerate(mod_channel_byte):
                                        if mod_bass_channel[counter]:
                                            # https://dobrian.github.io/cmp/topics/filters/lowpassfilter.html
                                            channel_byte_filtered = 0
                                            for byte in mod_channel_byte_last[counter]:  # find the sum of x amount of previous bytes
                                                channel_byte_filtered += byte
                                            channel_byte = channel_byte_filtered // mod_filter_order
                                        elif mod_filter:
                                            channel_byte = (channel_byte + mod_channel_byte_last[counter][0]) // 2
                                        if stereo:
                                            channel_byte_panned = Module._get_panned_bytes(channel_byte, mod_channel_pan[counter])
                                            channel_sum_left += channel_byte_panned[0] * 2
                                            channel_sum_right += channel_byte_panned[1] * 2
                                        else:
                                            channel_sum += channel_byte

                                        if not self._legacy:
                                            if mod_using_delay_channel:
                                                if mod_delay_counter == mod_delay_length - 1:  # i programmed this delay myself, no references!!
                                                    mod_delay_counter = 0
                                                else:
                                                    if mod_delay_channel[counter]:
                                                        mod_channel_delay_buffer[counter][mod_delay_counter] += channel_byte
                                                    if mod_delay_channel_fast[counter]:
                                                        delay_decay = 0.5
                                                    else:
                                                        delay_decay = 0.8
                                                    mod_channel_delay_buffer[counter][mod_delay_counter] *= delay_decay
                                                # reduce clicking
                                                delayed_byte = 0
                                                delay_filter_passes = 2
                                                for delay_filter in range(0, delay_filter_passes):
                                                    delayed_byte += mod_channel_delay_buffer[counter][mod_delay_counter - delay_filter]
                                                delayed_byte /= delay_filter_passes
                                                delayed_byte *= 1.2  # make the delay a smidge louder
                                                if not mod_delay_channel_fast[channel]:
                                                    delayed_byte *= 0.6  # reduce volume slightly for longer decays
                                                delayed_byte = int(0 - delayed_byte)
                                                if stereo:
                                                    channel_sum_right += delayed_byte  # delay only appears in the right channel - this is the intended behaviour! (it's a crude way of simulating stereo depth)
                                                else:
                                                    channel_sum += delayed_byte
                                                mod_delay_counter += 1

                                    if stereo:
                                        if channel_sum_left > 32767:
                                            channel_sum_left = 32767
                                        if channel_sum_left < -32768:
                                            channel_sum_left = 32768
                                        if channel_sum_right > 32767:
                                            channel_sum_right = 32767
                                        if channel_sum_right < -32768:
                                            channel_sum_right = -32768
                                    else:
                                        if channel_sum > 32767:
                                            channel_sum = 32767
                                        if channel_sum < -32768:
                                            channel_sum = 32768

                                    if stereo:
                                        channel_sum_left += 32768
                                        channel_sum_right += 32768
                                        channel_sum_left = (channel_sum_left + 32768) & 65535
                                        channel_sum_right = (channel_sum_right + 32768) & 65535
                                        channel_sum_stereo = channel_sum_left | (channel_sum_right << 16)
                                    else:
                                        channel_sum += 32768
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
                                if estimating_length:
                                    mod_overall_length += 1
                                else:
                                    mod_bytes_rendered += 1

                            if not mod_position_break and not mod_line_break and mod_pattern_delay_finished:
                                mod_lines_visited.append([mod_order_position, mod_line])

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
                                        if mod_song_length > 1:  # if the song is only one order long and there's a line break, stay on the same order
                                            mod_order_position += 1
                                            if mod_order_position > mod_song_length - 1:
                                                mod_order_position = 0
                                                if not mod_looped:
                                                    mod_looped = True
                                                    mod_loops += 1
                                        if [mod_order_position, mod_next_line] in mod_lines_visited:
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
                                        mod_jumps = [[mod_order_position, mod_line]]  # fixes "delayskip.mod" - probably not correct, but it works
                                        mod_orders_visited.clear()
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

                        mod_orders_visited.append(mod_order_position)  # this is only executed if the END of a pattern is reached with no breaks!!
                        if not mod_line_break:  # position breaks reset the line anyway
                            mod_line = 0
                        if mod_song_length > 1:
                            mod_order_position += 1
                            if mod_order_position == mod_song_length:  # reached the very last order?
                                mod_order_position = 0
                                mod_pointer = mod_pattern_offsets[mod_order[0]]
                                mod_line = 0
                                if not mod_looped:
                                    mod_looped = True
                                    mod_loops += 1
                                    mod_jumps.clear()
                                    mod_orders_visited.clear()
                        else:
                            if not mod_looped:
                                mod_looped = True
                                mod_loops += 1
                        if mod_loops > self._loops - 1:  # copypasta SSSSHHHHH (but this is for when the pattern ends, not per line... so if you're line breaking/position breaking this won't be reached)
                            mod_order_position = mod_song_length  # end
                            mod_line = mod_lines
                        mod_pointer = mod_pattern_offsets[mod_order[mod_order_position]]

                    if (self._render_file is not None and not while_condition) or (self._render_file is not None and self._render_channels) and not estimating_length:
                        if self._render_channels:
                            dir_name = os.path.dirname(self._render_file)
                            if dir_name != "":
                                dir_name += "/"
                            base_name = os.path.splitext(os.path.basename(self._render_file))[0][:-2]  # file name, minus the _1
                            file_name = f"{dir_name}{base_name}_{channel_current + 1}.wav"
                        else:
                            file_name = self._render_file
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

                    if estimating_length:
                        estimating_length = False
                        start_time = time.perf_counter()
                        estimated_length = mod_overall_length / self._sample_rate
                        estimated_length_minutes = estimated_length // 60
                        estimated_length_seconds = estimated_length % 60
                        if self._play_mode == "info":
                            while_condition = False
                        self._sample_rate = sample_rate_temp
                        mod_ms_per_tick = self._mod_get_tempo_length()

                if self._render_file is not None:
                    end_time = time.perf_counter() - start_time
                    minutes = int(end_time / 60)
                    seconds = end_time % 60
                    if not self._quiet:
                        print()
                        stringy = "Rendered in "
                        if minutes == 0:
                            if seconds == 1:
                                stringy += "1 second!"
                            else:
                                stringy += f"{seconds:.2f} seconds!"
                        elif minutes == 1:
                            stringy += f"1 minute, {seconds:.2f} seconds!"
                        else:
                            stringy += f"{minutes} minutes, {seconds:.2f} seconds!"
                        print(stringy)
                else:
                    if self._play_mode != "info":
                        if not self._quiet:
                            print()
                            print("Done!")
                        stream.stop_stream()
                        stream.close()
                        pya.terminate()

            if self._play_mode == "info":
                print("Module:             ")
                print(f"\tName: {mod_name}")
                print(f"\tPatterns: {mod_pattern_amount}")
                order_string = f"{mod_song_length} order"
                if mod_song_length > 1:
                    order_string += "s"
                print(f"\tLength: {order_string}")
                print(f"\tChannels: {mod_channels} - {mod_type_string}")
                print(f"\tEstimated length: {int(estimated_length_minutes)}m {int(estimated_length_seconds)}s")
                print("Samples:")
                for sample in mod_unique_samples:
                    looping_string = ""
                    if sample[1]["loop_length"] == 2 and sample[1]["loop_start"] == 0:
                        looping_string = "no loop"
                    else:
                        looping_string = f"Loop start: {sample[1]['loop_start']}, Loop length: {sample[1]['loop_length']}"
                    finetune = sample[1]["finetune"]
                    if finetune > 7:
                        finetune = finetune - 16
                    sample_number = str(sample[0] + 1).rjust(2, " ")
                    print(f"\t{sample_number}. {sample[1]['name']}")
                    print(f"\t\tLength: {sample[1]['length']}, {looping_string}, Finetune: {finetune}, Volume: {sample[1]['volume']}")

    def set_sample_rate(self, rate):
        self._sample_rate = rate

    def set_nb_of_loops(self, nb_of_loops):
        self._loops_init = nb_of_loops

    def set_play_mode(self, play_mode):
        self._play_mode = play_mode

    def set_verbose(self, flag):
        self._verbose = flag

    def set_buffer_size(self, size):
        self._buffer_size = size

    def set_quiet(self, flag):
        self._quiet = flag

    def set_legacy(self, flag):
        self._legacy = flag

    def set_amplify(self, factor):
        self._amplify = factor

    def set_interpolate(self, flag):
        self._interpolate = flag

    def play(self):
        self._run()

    def render_to(self, filepath, separate_channels=False):
        self._render_file = filepath
        self._render_channels = separate_channels
        self._run()
