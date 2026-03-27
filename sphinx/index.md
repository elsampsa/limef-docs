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
    camtr[USBCameraTR]
    uploadff(UploadGPUFF)
    d2t(Dec2TensorFF)
    pyif[TensorPythonInterface]
    t2d(Tensor2DecFF)
    encff(EncFF)
    rtpmux(RTPMuxerFF)
    rtsptr[RTSPServerTR]

    camtr --- uploadff
    uploadff --- d2t
    d2t -->|TensorFrame CUDA| pyif
    pyif --- t2d
    t2d --- encff
    encff --- rtpmux
    rtpmux --> rtsptr

    classDef thread fill:#4a90d9,stroke:#2c5f8a,color:#fff
    classDef pytr   fill:#7b5ea7,stroke:#4a3570,color:#fff
    classDef ff     fill:#5ba85a,stroke:#3d6e3d,color:#fff
    class camtr,rtsptr thread
    class pyif pytr
    class uploadff,d2t,t2d,encff,rtpmux ff
```
We could also fork that pipeline from any node: think of writing the stream to disk, sending it to various machine vision processes, etc.

For more complex pipelines, please take a look at the [python example apps](https://github.com/elsampsa/limef-apps/tree/master/python).

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
