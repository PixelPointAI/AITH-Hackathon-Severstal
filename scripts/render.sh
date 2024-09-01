#!/bin/bash

blender-3.6.0-linux-x64/blender \
--background \
--python \
tools/render.py -- path/to/object.obj save_dir 5.0 20.0
