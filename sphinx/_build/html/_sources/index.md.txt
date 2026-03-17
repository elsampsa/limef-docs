# Limef

```{eval-rst}
.. meta::
   :description: A linux mediastreaming framework, based on ffmpeg
   :keywords: media streaming ffmpeg
```

*WARNING: heavily UNDER CONSTRUCTION / WORK IN PROGRESS*

Limef is a **Li**nux **Me**dia Streaming **F**ramework

Limef is a C++ media streaming library with python bindings for creating complex
media streaming pipelines.

It is similar to gstreamer, deepstream and libValkka, but goes a step further in possibilities and ease of use.

Here is an example where we capture USB camera, upload the bitmaps to GPU, manipulate the image, encode it to H264 and then
serve the modified video stream through an RTSP server for transmission LAN.  The image manipulation/analysis part can be done in C++ or Python
(the filterchain "visits" the python side):

```{mermaid}
flowchart TD
    cam["USBCameraThread"]
    upload["UploadGPUFrameFilter"]
    d2t["DecodedToTensorFrameFilter"]
    py["TensorPythonInterface"]
    t2d["TensorToDecodedFrameFilter"]
    enc["EncodingFrameFilter"]
    rtp["RTPMuxerFrameFilter"]
    rtsp["RTSPServerThread"]

    cam --> upload --> d2t --> py --> t2d --> enc --> rtp --> rtsp
```

Some Limef features:

- Media streams and stream metadata move through a unified framefilter pipeline
- Threads are integrated into the pipeline in an opaque manner for the API user
- Media streams can be "uploaded" to GPU and "downloaded" back to CPU
- Decoded bitmaps can be operated both on GPU and CPU using your favorite tensor library and integrated into your machine vision applications
- Software and hardware decoders and encoders (mainly CUDA-based)
- Special emphasis on live streaming
- A flexible plugin system for integrating third-party libraries

Limef has been carefully vibe-coded in C++ using my decade+ experience in live media streaming and machine vision problems.

Limef is based on ffmpeg.

```{toctree}
:maxdepth: 2

self
intro
concepts
under_the_hood
tutorial/index
api/index
distribution
```
