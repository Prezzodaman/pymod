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

import traceback
import argparse
import pymod


# -- This enables more debugging information for exceptions.
_debug_on: bool = False


def main():
    global _debug_on

    module = None

    try:
        _debug_on = True

        parser = argparse.ArgumentParser(description="Plays a .mod file")
        parser.add_argument("input_file", type=argparse.FileType("r"), help="The name of the module")
        parser.add_argument("sample_rate", type=int, help="Sample rate for playback/rendering")
        parser.add_argument("play_mode", type=str, help="Selects a different play mode: " + ", ".join(pymod.Module.play_modes()))
        parser.add_argument("-r", "--render", type=argparse.FileType("w"), help="Renders the module to a wave file. If rendering multiple channels, end the filename with _1 (e.g. pymod_1.wav) and the files will be numbered sequentially")
        parser.add_argument("-l", "--loops", type=int, help="The amount of times to loop the module")
        parser.add_argument("-v", "--verbose", action="store_true", help="If playing, this displays the pattern as it's being played. If rendering, this shows the progress of each pattern.")
        parser.add_argument("-c", "--channels", action="store_true", help="Renders each channel to its own file. If playing, this does nothing. The channel volume is reduced, so the result is identical when all channels are mixed together.")
        parser.add_argument("-b", "--buffer", type=int, default=pymod.Module.buffer_size_default(), help=f"Change the buffer size for realtime playback (default is {pymod.Module.buffer_size_default()})")
        parser.add_argument("-q", "--quiet", action="store_true", help="Shows absolutely no info while playing/rendering a module")
        args = parser.parse_args()

        module = pymod.Module(args.input_file.name)
        module.set_sample_rate(args.sample_rate)
        module.set_nb_of_loops(args.loops)
        module.set_play_mode(args.play_mode.lower())
        module.set_verbose(args.verbose)
        module.set_buffer_size(args.buffer)
        module.set_quiet(args.quiet)

        if module is not None:
            if args.render is not None:
                module.render_to(args.render.name, args.channels)
            else:
                module.play()

    except Exception as e:
        if _debug_on:
            print(traceback.format_exc())

        print(e)
    except KeyboardInterrupt:
        print("Execution interrupted by user.")
        pass


if __name__ == "__main__":
    main()
