#!/bin/bash

render-cli \
--blender-path blender-3.6.0-linux-x64/blender \
--object-path path/to/object.obj \
--output-dir save_dir \
--distance-between-cameras 5.0 \
--distance-from-object 15.0 \
--num-pairs 10
