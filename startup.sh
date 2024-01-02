#!/bin/bash

# Install FiftyOne plugins
fiftyone plugins download https://github.com/jacobmarks/image-quality-issues/
fiftyone plugins download https://github.com/jacobmarks/image-deduplication-plugin
fiftyone plugins download https://github.com/jacobmarks/zero-shot-prediction-plugin
fiftyone plugins download https://github.com/jacobmarks/active-learning-plugin

# Install FiftyOne plugins requirements
fiftyone plugins requirements @jacobmarks/active_learning --install

# Start Jupyter Notebook in the background
jupyter lab --ip 0.0.0.0 --no-browser --allow-root &

# Start FiftyOne in the background
fiftyone app launch --address 0.0.0.0 --remote &

# Keep the container running
tail -f /dev/null
