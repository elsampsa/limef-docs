# Key Concepts and Definitions

*Learn the principles of building multithreaded filterchains*

## Pipelines, streams, frames

A media streaming pipeline consists of independently running **threads** that produce and consume **frames**.

A stream consists of a continuous stream of **frames**.

Frames can be almost anything:

- Encoded images (say, H264 or H265 video)
- Decoded images, i.e. just bitmaps in various formats (interleaved, planar)
- Encoded or decoded audio (i.e., mp3 or wav, etc.)
- Metadata about the frames creating a stream
- Messages / signals

In Limef we emphasize this universal aspect of frames: they can be metadata, commands, almost any object
that has an **id number** and **a timestamp**.

The available frame types are identified by the {cpp:enum}`Limef::frame::FrameClass` enumeration.
Each frame class corresponds to a subclass of {cpp:class}`Limef::frame::Frame`:

| FrameClass | Class |
|---|---|
| `FrameClass::Packet` | {cpp:class}`Limef::frame::PacketFrame` — encoded video/audio packets |
| `FrameClass::Decoded` | {cpp:class}`Limef::frame::DecodedFrame` — raw bitmaps or PCM audio |
| `FrameClass::Codec` | {cpp:class}`Limef::frame::CodecFrame` — codec parameters |
| `FrameClass::Signal` | {cpp:class}`Limef::frame::SignalFrame` — thread control commands |
| `FrameClass::Stream` | {cpp:class}`Limef::frame::StreamFrame` — stream metadata for encoders |
| `FrameClass::SDP` | {cpp:class}`Limef::frame::SDPFrame` — SDP for RTSP |
| `FrameClass::RTPPacket` | {cpp:class}`Limef::frame::RTPPacketFrame` — RTP/RTCP packets |
| `FrameClass::Tensor` | {cpp:class}`Limef::frame::TensorFrame` — N-plane tensor, CPU or GPU |

## Threads

A thread consumes certain kind of frames and produces another and/or different kind of frames.

**Producer threads** only produce, while **terminal threads** only consume.

An example of a producing thread is {cpp:class}`Limef::thread::MediaFileThread`, which reads a media file
and pushes {cpp:class}`Limef::frame::PacketFrame`s downstream.

A terminal thread is for example the {cpp:class}`Limef::rtsp::RTSPServerThread` that serves the media
stream over the internet.

Each thread exposes an input and output **framefilter** via
{cpp:func}`Limef::thread::Thread::getInput` and {cpp:func}`Limef::thread::Thread::getOutput`.
These are the **connection points** where threads plug into the **filterchain**.

## Framefilters

A **framefilter** takes an input frame and produces an output frame.
The input and output frames can be of the same or of a different frame type.

An example of the simplest framefilter is the {cpp:class}`Limef::ff::DumpFrameFilter` that dumps information
about the frame into the terminal.

Framefilters can be chained with the `cc` method ("connect chain"):

```cpp
InfoFrameFilter     info("info");
DumpFrameFilter     dump("dump");
DecodingFrameFilter decode("decode");

// Chain them: info -> dump -> decode
info.cc(dump).cc(decode);

// Start the cascade with a single go() call:
info.go(frame);
```

The cascade calls `go()` on each filter in turn.  Each filter may transform the frame, then calls
`pass()` to forward it downstream.

For a one-to-many split, use {cpp:class}`Limef::ff::SplitFrameFilter`:

```cpp
SplitFrameFilter split("split");
DumpFrameFilter  branch1("branch1");
DumpFrameFilter  branch2("branch2");

split.cc(branch1);
split.cc(branch2);        // or: split.cm({&branch1, &branch2})
// later: split.dc(branch1);  // disconnect one branch at runtime
```

{cpp:class}`Limef::ff::SplitFrameFilter` is thread-safe — you can call `cc` / `dc` after threads have started.

## Filterchains

### Upstream and downstream

```
upstream      downstream
ff1 -> ff2 -> ff3
```

When `ff1.go(frame)` is called, these rules are strictly followed:

- Frames received from upstream are **never modified** by downstream framefilters — they can be copied, read, or passed on, but not mutated
- A framefilter may own internal frames which it passes downstream, but their ownership stays with that framefilter

### Connecting threads

A thread starts a filterchain at its output and the chain ends at the next thread's input:

```
ProducerThread.getOutput() ──► ff1 ──► ff2 ──► ConsumerThread.getInput()
```

Use {cpp:func}`Limef::thread::Thread::getOutput` and {cpp:func}`Limef::thread::Thread::getInput`
to wire threads into the chain.

Almost any kind of information flows in a filterchain.  Data frames
({cpp:class}`Limef::frame::PacketFrame`, {cpp:class}`Limef::frame::DecodedFrame`, etc.) carry
media payload, while {cpp:class}`Limef::frame::SignalFrame` carries control commands (start, stop,
flush, parameter changes) — all through the same `go()` call, no separate control bus needed.

### A complete example

Encoded frames (H265) come from a file-reading thread.  The stream is forked: one branch is
decoded for analysis, the other goes to a muxer.

```{mermaid}
flowchart TD
    src["MediaFileThread"]
    split["SplitFrameFilter"]
    decode["DecodingFrameFilter"]
    analyze["analysis filterchain"]
    mux["MuxerFrameFilter"]

    src --> split
    split --> decode --> analyze
    split --> mux
```

In C++:

```cpp
DumpFrameFilter     analyzer("analyzer");
MuxerFrameFilter    muxer("muxer", mux_ctx);
DecodingFrameFilter decode("decode");
SplitFrameFilter    split("split");

decode.cc(analyzer);
split.cc(decode);
split.cc(muxer);

MediaFileThread source("source", media_ctx);
source.getOutput().cc(split);

source.start();
```

As YAML:

```yaml
source:
    class: MediaFileThread
    connect: split

split:
    class: SplitFrameFilter
    connect:
        - decode
        - muxer

decode:
    class: DecodingFrameFilter
    connect: analyzer

muxer:
    class: MuxerFrameFilter
```

For a deeper look at how threads and framefifos work under the hood, see {doc}`under_the_hood`.
