#
# Copyright (c) 2023-present Presley Peters (Prezzo).
# Pymod is licensed under GPL v3.0.
#
# This file is part of pymod.
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
