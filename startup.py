import fiftyone as fo


# Enable connections from remote hosts
session = fo.launch_app(remote=True, address="0.0.0.0")
