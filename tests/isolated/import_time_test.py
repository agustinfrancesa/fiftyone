"""
Test that fiftyone can be imported in a reasonable amount of time.
"""

import warnings
import time

# TODO: decrease these once the DB service is started on-demand?
IMPORT_WARN_THRESHOLD = 1.75
IMPORT_ERROR_THRESHOLD = 5


def test_import_time(capsys):
    t1 = time.perf_counter()
    import fiftyone

    time_elapsed = time.perf_counter() - t1
    message = "`import fiftyone` took %f seconds" % time_elapsed
    if time_elapsed > IMPORT_ERROR_THRESHOLD:
        raise RuntimeError(message)
    elif time_elapsed > IMPORT_WARN_THRESHOLD:
        # disable stdout capture temporarily
        with capsys.disabled():
            # message must follow this format:
            # https://docs.github.com/en/actions/reference/workflow-commands-for-github-actions#setting-a-warning-message
            print("\n::warning::%s\n" % message)
            warnings.warn(message)
