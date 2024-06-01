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

import wave

# -- We need to import from our parent folder here.
sys.path.append(os.path.join(sys.path[0], '..'))

import pymod    # noqa: E402


# -- Utility functions
def check_wave_file(wave_file):
    '''Makes sure the wav file is the correct type/format.'''
    assert wave_file.getnchannels() == 2
    assert wave_file.getsampwidth() == 2
    assert wave_file.getframerate() == pymod.Module.render_test_sample_rate()
    assert wave_file.getcomptype() == 'NONE'


def read_wave_file(filepath):
    data = []
    print(f'Check {filepath}')
    with wave.open(filepath, "rb") as wave_file:
        check_wave_file(wave_file)
        data = wave_file.readframes(wave_file.getnframes())
        wave_file.close()

    return data


def get_nb_of_samples(wave_file_data):
    return len(wave_file_data) // 4


def sign_extend_int16(value):
    return (((value & 0xFFFF) + 0x8000) & 0xffff) - 0x8000


def get_left_sample(wave_file_data, index):
    sample_index = index * 4
    # print(f'-=> L {index} : {wave_file_data[sample_index]:02x} {wave_file_data[sample_index + 1]:02x} {(((wave_file_data[sample_index + 1] << 8) | wave_file_data[sample_index]) & 0xFFFF):04x}')
    return sign_extend_int16((wave_file_data[sample_index + 1] << 8) | wave_file_data[sample_index])


def get_right_sample(wave_file_data, index):
    sample_index = index * 4
    # print(f'-=> R {index} : {wave_file_data[sample_index + 2]:02x} {wave_file_data[sample_index + 3]:02x} {(((wave_file_data[sample_index + 3] << 8) | wave_file_data[sample_index + 2]) & 0xFFFF):04x}')
    return sign_extend_int16((wave_file_data[sample_index + 3] << 8) | wave_file_data[sample_index + 2])


def get_left_sample_raw(wave_file_data, index):
    sample_index = index * 4
    return (wave_file_data[sample_index + 1] << 8) | wave_file_data[sample_index]


def get_right_sample_raw(wave_file_data, index):
    sample_index = index * 4
    return (wave_file_data[sample_index + 3] << 8) | wave_file_data[sample_index + 2]


def write_sample(wave_file_data, left_sample, right_sample):
    if left_sample > 32767:
        left_sample = 32767
    if left_sample < -32768:
        left_sample = -32768

    left_sample &= 0xFFFF

    wave_file_data.append(left_sample & 255)
    wave_file_data.append(left_sample >> 8)

    if right_sample > 32767:
        right_sample = 32767
    if right_sample < -32768:
        right_sample = -32768

    right_sample &= 0xFFFF

    wave_file_data.append(right_sample & 255)
    wave_file_data.append(right_sample >> 8)


def write_wave_file(filepath, wave_file_data):
    with wave.open(filepath, "wb") as wave_file:
        wave_file.setnchannels(2)
        wave_file.setsampwidth(2)
        wave_file.setframerate(pymod.Module.render_test_sample_rate())
        wave_file.writeframesraw(bytearray(wave_file_data))


# -- List of modules to test
modules_list = [
    'arpeggio', 'fineport', 'nosamp', 'port2', 'tremolo',
    'delay', 'fx', 'offset', 'port3', 'vibwave',
    'delay2', 'glissando', 'offsetweird', 'portfunny', 'vol',
    'delaysim', 'line', 'pan', 'position', 'volslide',
    'filter', 'loop', 'patdelay', 'pwm', 'volslide2',
    'fine', 'loud', 'patloop2', 'simpy', 'volume2',
    'fine2', 'nonexistence', 'port1', 'test', 'weirdthing',
    'cuts', 'ode2ptk', 'wraparound', 'wraparound2', 'breaks',
    'breaks2', 'volall', 'arptimings', 'timestretch', 'arpdesync',
    'extended', 'portlimit', 'loopchange', 'loud2', 'loud3',
    'basschan', 'loopchange2'
]


# -- Tests
@pytest.mark.parametrize("filename", modules_list)
def test_render(filename, tmp_path):
    module_filepath = os.path.join(sys.path[0], 'tests', 'modules', f'{filename}.mod')
    assert os.path.exists(module_filepath)

    wav_filename = filename + '.wav'
    wav_filepath = os.path.join(sys.path[0], 'tests', 'wavs', wav_filename)
    assert os.path.exists(wav_filepath)

    temp_file = os.path.join(tmp_path, 'pymod-test-' + wav_filename)

    module = pymod.Module(module_filepath)
    assert module is not None

    # -- This makes sure the random offset value used in some effect matches the one for the test files we compare against
    random.seed(pymod.Module.render_test_random_seed())

    module.set_sample_rate(pymod.Module.render_test_sample_rate())
    module.set_play_mode('stereo_hard')
    module.render_to(temp_file)

    assert filecmp.cmp(wav_filepath, temp_file)

    os.remove(temp_file)


@pytest.mark.parametrize("filename", modules_list)
def test_render_channels(filename, tmp_path):
    module_filepath = os.path.join(sys.path[0], 'tests', 'modules', f'{filename}.mod')
    assert os.path.exists(module_filepath)

    temp_file_prefix = os.path.join(tmp_path, f'pymod-test-{filename}')
    temp_file = temp_file_prefix + '_1.wav'

    module = pymod.Module(module_filepath)
    assert module is not None

    # -- This makes sure the random offset value used in some effect matches the one for the test files we compare against
    random.seed(pymod.Module.render_test_random_seed())

    module.set_sample_rate(pymod.Module.render_test_sample_rate())
    module.set_play_mode('stereo_hard')
    module.set_quiet(True)
    module.render_to(temp_file, True)

    # -- We mix all the resulting channels into one stereo file
    channel_data = []
    channels = 0

    # it would be nicer to have pymod return the number of channels, but i couldn't figure that out
    for channel in range(1, 9):
        if os.path.exists(f"{temp_file_prefix}_{channel}.wav"):
            channel_data.append(read_wave_file(f"{temp_file_prefix}_{channel}.wav"))
            channels += 1
    channel_length = get_nb_of_samples(channel_data[0])

    mixed_data = []
    for position in range(0, channel_length):
        mixed_left = 0
        mixed_right = 0
        for channel in range(0, channels):
            mixed_left += get_left_sample(channel_data[channel], position)
            mixed_right += get_right_sample(channel_data[channel], position)
        write_sample(mixed_data, mixed_left, mixed_right)

    temp_file = temp_file_prefix + '.wav'
    write_wave_file(temp_file, mixed_data)

    wav_filepath = os.path.join(sys.path[0], 'tests', 'wavs', f'{filename}.wav')
    assert os.path.exists(wav_filepath)

    # -- Mixed and generated version should match
    assert filecmp.cmp(wav_filepath, temp_file)

    os.remove(temp_file)
