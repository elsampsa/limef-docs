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

### Diagram notation

Diagrams follow these conventions:

- **Thread** — rectangle `[Name]`, abbreviated `...TR`.
  Incoming edge uses an arrow (`-->`) to mark the thread boundary: the frame is copied into a FrameFifo before the thread processes it.
- **FrameFilter** — rounded rectangle `(Name)`, abbreviated `...FF`.
  Incoming edge uses a plain line (`---`) to show synchronous, same-chain forwarding — no copy, no boundary.
- **Block** — subroutine box `[[Name]]`.
  Always uses an arrow on incoming edges since blocks always contain internal threads.

```{mermaid}
flowchart LR
    ff1(UpstreamFF) --- ff2(AnotherFF) --> thr[ConsumerTR]

    classDef thread fill:#4a90d9,stroke:#2c5f8a,color:#fff
    classDef ff     fill:#5ba85a,stroke:#3d6e3d,color:#fff
    class thr thread
    class ff1,ff2 ff
```

FF→FF: no arrow (same chain).  FF→Thread: arrow (FrameFifo boundary).

### YAML declarations

Pipelines can be described in YAML.  Inline nesting reflects the filterchain topology directly — each node's downstream is nested under its `connect:` key:

```yaml
source:              # top-level named node
    class: MediaFileThread
    connect:
        split:       # inline anonymous node, nested under source
            class: SplitFrameFilter
            connect:
                decode:
                    class: DecodingFrameFilter
                    connect:
                        analyzer:
                            class: DumpFrameFilter
                muxer:       # second branch of the split
                    class: MuxerFrameFilter
```

`connect:` reference rules:
- **bare name** → top-level named node: `connect: encoderblock`
- **`./name`** → sibling member within the same block: `connect: ./cuda2dec`
- **`../name`** → sibling of the parent (one level up): `connect: ../output`  *(used from inside switch branches)*

### A complete example

Encoded frames (H265) come from a file-reading thread.  The stream is forked: one branch is
decoded for analysis, the other goes to a muxer.

```{mermaid}
flowchart TD
    src[MediaFileTR]
    split(SplitFF)
    decode(DecodingFF)
    analyze(DumpFF)
    mux(MuxerFF)

    src --- split
    split --- decode
    decode --- analyze
    split --- mux

    classDef thread fill:#4a90d9,stroke:#2c5f8a,color:#fff
    classDef ff     fill:#5ba85a,stroke:#3d6e3d,color:#fff
    class src thread
    class split,decode,analyze,mux ff
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

For a deeper look at how threads and framefifos work under the hood, see {doc}`under_the_hood`.
