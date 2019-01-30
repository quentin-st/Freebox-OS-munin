#!/usr/bin/env python3

import os
import modes

for mode in modes.modes:
    if os.path.isfile(mode):
        print("Symlink {} already exists".format(mode))
    else:
        print("Create symlink:", mode)
        os.symlink("main.py", mode)
