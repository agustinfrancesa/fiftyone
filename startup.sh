#!/bin/bash

fiftyone app launch --address 0.0.0.0 --remote
jupyter lab --ip 0.0.0.0 --no-browser --allow-root

