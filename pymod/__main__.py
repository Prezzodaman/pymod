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

from .pymod import pymod


# -- This enables more debugging information for exceptions.
_debug_on: bool = False


def main():
    global _debug_on

    player = None

    try:
        _debug_on = True

        player = pymod()

        if player is not None:
            player.parse_args()
            player.run()

    except Exception as e:
        if _debug_on:
            print(traceback.format_exc())

        print(e)
    except KeyboardInterrupt:
        print('Execution interrupted by user.')
        pass

    if player is not None:
        player.shutdown()


if __name__ == '__main__':
    main()
