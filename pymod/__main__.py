#
# Copyright (c) 2023-present Presley Peters (Prezzo).
#
# This file is part of pymod.
#

from .pymod import pymod


def main():
    player = None

    try:
        player = pymod()

        if player is not None:
            player.main()
    except Exception as e:
        print(e)
    except KeyboardInterrupt:
        print('Execution interrupted by user.')
        pass

    if player is not None:
        player.shutdown()


if __name__ == '__main__':
    main()
