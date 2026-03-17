## A Media Streaming Framework

### What is a "Media Streaming Framework" anyway?

Employing AI machine vision systems at scale in the cloud and in the edge devices is a challenging problem.

You need to deal with high bitrate (high resolution and frames per second) media streams, network outages and packet bursts (for live streams over the internet) and sharing the decoded streams and images between several AI/ML processes.  

This requires a sophisticated software architecture of multithreading, queques and stream replication, just to name a few complications.  All this "under-the-hood" infrastructure needs to interact with the main components of your software, user interfaces, web apis, etc.

A media streaming framework handles all this gruntwork of multithreading, queques, mutexes and semaphores under-the-hood and hides it behind and API.  You just need to do the piping, and describe how the stream is encoded, decoded, sent to GPU (for analysis or encoding/decoding) and served.

For specialized ML/AI tasks, you write dedicated threads, conforming to the framework's API, and they become a natural part of the pipeline.

### Why not just use ffmpeg?

You would typically start with ffmpeg C libraries that have all the necessary infra to decode and encode media streams.

However, ffmpeg doesn't provide a framework for stream replication, sharing and serving.  You'd need to write all that piping yourself.

### What can Limef do?

Limef is Work In Progress and I will be adding new features along the way as they fit my personal goals and interests.

At the moment working modules are:

- Streaming from files and USB cameras
- Software and hardware (cuda and vaapi) encoding and decoding
- Streaming bitmap and tensor frames to/from GPU
- Image analysis on CPU and GPU (for cuda)
- Muxing into various formats and also into RTP
- RTSP server
- Write your own Limef-based code in cpp or python
- Limef app and plugin examples

In the near future:

- Websocket server
- Streaming from IP cameras
- WebRTC server

Long-term:

- Video streaming from the pipeline to desktop environment and to PyQt (libValkka-style)
- Local disk and cloud storage
- Ready for video-management systems
