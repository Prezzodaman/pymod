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

import pytest
import sys
import os
import filecmp
import random

# -- We need to import from our parent folder here.
sys.path.append(os.path.join(sys.path[0], '..'))

import pymod    # noqa: E402


# -- List of modules to test
modules_list = [
    'arpeggio.mod', 'fineport.mod', 'nosamp.mod', 'port2.mod', 'tremolo.mod',
    'delay.mod', 'fx.mod', 'offset.mod', 'port3.mod', 'vibwave.mod',
    'delay2.mod', 'glissando.mod', 'offsetweird.mod', 'portfunny.mod', 'vol.mod',
    'delaysim.mod', 'line.mod', 'pan.mod', 'position.mod', 'volslide.mod',
    'filter.mod', 'loop.mod', 'patdelay.mod', 'pwm.mod', 'volslide2.mod',
    'fine.mod', 'loud.mod', 'patloop2.mod', 'simpy.mod', 'volume2.mod',
    'fine2.mod', 'nonexistence.mod', 'port1.mod', 'test.mod', 'weirdthing.mod'
]


# -- Tests
@pytest.mark.parametrize("filename", modules_list)
def test_render(filename, tmp_path):
    module_filepath = os.path.join(sys.path[0], 'tests', 'modules', filename)
    assert os.path.exists(module_filepath)

    wav_filename = os.path.splitext(filename)[0] + '.wav'
    wav_filepath = os.path.join(sys.path[0], 'tests', 'wavs', wav_filename)
    assert os.path.exists(wav_filepath)

    temp_file = os.path.join(tmp_path, 'pymod-test-' + wav_filename)

    # -- This makes sure the random offset value used in some effect matches the one for the test files we compare against
    random.seed(23)

    module = pymod.Module(module_filepath)
    assert module is not None

    module.set_sample_rate(44100)
    module.set_play_mode('stereo_hard')
    module.render_to(temp_file)

    assert filecmp.cmp(wav_filepath, temp_file)

    os.remove(temp_file)
