#!/bin/bash

# Start Jupyter Notebook in the background
jupyter lab --ip 0.0.0.0 --no-browser --allow-root &

# Start FiftyOne in the background
fiftyone app launch --address 0.0.0.0 --remote &

# Keep the container running
tail -f /dev/null
