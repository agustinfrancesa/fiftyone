"""
Utilities for working with
`Lightning Flash <https://github.com/PyTorchLightning/lightning-flash>`_.

| Copyright 2017-2021, Voxel51, Inc.
| `voxel51.com <https://voxel51.com/>`_
|
"""
import inspect
import itertools

import numpy as np

import fiftyone.core.metadata as fom
import fiftyone.core.utils as fou

fou.ensure_lightning_flash()
import flash
import flash.core.classification as fc
import flash.image as fi
import flash.image.detection.serialization as fds
import flash.image.segmentation.serialization as fss


_SUPPORTED_MODELS = (
    fi.ImageClassifier,
    fi.ObjectDetector,
    fi.SemanticSegmentation,
)

_SUPPORTED_EMBEDDERS = (fi.ImageEmbedder,)


def apply_flash_model(
    samples,
    model,
    label_field="predictions",
    confidence_thresh=None,
    store_logits=False,
    batch_size=None,
    num_workers=None,
):
    """Applies the given
    :class:`Lightning Flash model <flash:flash.core.model.Task>` to the samples
    in the collection.

    Args:
        samples: a :class:`fiftyone.core.collections.SampleCollection`
        model: a :class:`flash:flash.core.model.Task`
        label_field ("predictions"): the name of the field in which to store
            the model predictions. When performing inference on video frames,
            the "frames." prefix is optional
        confidence_thresh (None): an optional confidence threshold to apply to
            any applicable labels generated by the model
        store_logits (False): whether to store logits for the model
            predictions. This is only supported when the provided ``model`` has
            logits
        batch_size (None): an optional batch size to use. If not provided, a
            default batch size is used
        num_workers (None): the number of workers for the data loader to use
    """
    serializer = _get_serializer(model, confidence_thresh, store_logits)

    # Running `Trainer().predict()` seems to cause `model.data_pipeline` to be
    # garbage-collected after inference, so we restore it to its original value
    data_pipeline = model.data_pipeline

    with fou.SetAttributes(
        model, data_pipeline=data_pipeline, serializer=serializer
    ):
        kwargs = dict(preprocess=model.preprocess, num_workers=num_workers)
        if batch_size is not None:
            kwargs["batch_size"] = batch_size

        datamodule = fi.ImageClassificationData.from_fiftyone_datasets(
            predict_dataset=samples, **kwargs
        )
        predictions = flash.Trainer().predict(model, datamodule=datamodule)
        predictions = list(itertools.chain.from_iterable(predictions))

        samples.set_values(label_field, predictions)


def compute_flash_embeddings(
    samples, model, embeddings_field=None, batch_size=None, num_workers=None
):
    """Computes embeddings for the samples in the collection using the given
    :class:`Lightning Flash model <flash:flash.core.model.Task>`.

    This method only supports applying an
    :class:`flash:flash.image.ImageEmbeder` to an image collection.

    If an ``embeddings_field`` is provided, the embeddings are saved to the
    samples; otherwise, the embeddings are returned in-memory.

    Args:
        samples: a :class:`fiftyone.core.collections.SampleCollection`
        model: a :class:`flash:flash.image.ImageEmbeder`
        embeddings_field (None): the name of a field in which to store the
            embeddings
        batch_size (None): an optional batch size to use. If not provided, a
            default batch size is used
        num_workers (None): the number of workers for the data loader to use

    Returns:
        one of the following:

        -   ``None``, if an ``embeddings_field`` is provided
        -   a ``num_samples x num_dim`` array of embeddings, if
            ``embeddings_field`` is None
    """
    if not isinstance(model, _SUPPORTED_EMBEDDERS):
        raise ValueError(
            "Unsupported model type %s. Supported model types are %s"
            % (type(model), _SUPPORTED_EMBEDDERS)
        )

    # Running `Trainer().predict()` seems to cause `model.data_pipeline` to be
    # garbage-collected after inference, so we restore it to its original value
    data_pipeline = model.data_pipeline

    with fou.SetAttributes(model, data_pipeline=data_pipeline):
        # equivalent(?) but no progress bar...
        # filepaths = samples.values("filepath")
        # embeddings = model.predict(filepaths)

        kwargs = dict(preprocess=model.preprocess, num_workers=num_workers)
        if batch_size is not None:
            kwargs["batch_size"] = batch_size

        datamodule = fi.ImageClassificationData.from_fiftyone_datasets(
            predict_dataset=samples, **kwargs
        )
        embeddings = flash.Trainer().predict(model, datamodule=datamodule)
        embeddings = list(itertools.chain.from_iterable(embeddings))

        if embeddings_field is not None:
            samples.set_values(embeddings_field, embeddings)
            return

        return np.stack(embeddings)


def _get_serializer(model, confidence_thresh, store_logits):
    if isinstance(model, fi.ImageClassifier):
        prev_args = dict(inspect.getmembers(model.serializer))

        kwargs = {
            "multi_label": prev_args.get("multi_label", False),
            "store_logits": store_logits,
        }

        if "threshold" in prev_args:
            kwargs["threshold"] = prev_args["threshold"]

        if confidence_thresh is not None:
            kwargs["threshold"] = confidence_thresh

        return fc.FiftyOneLabels(**kwargs)

    if isinstance(model, fi.ObjectDetector):
        return fds.FiftyOneDetectionLabels(threshold=confidence_thresh)

    if isinstance(model, fi.SemanticSegmentation):
        return fss.FiftyOneSegmentationLabels()

    raise ValueError(
        "Unsupported model type %s. Supported model types are %s"
        % (type(model), _SUPPORTED_MODELS)
    )
