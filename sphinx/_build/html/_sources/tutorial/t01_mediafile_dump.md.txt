# Tutorial 1: Streaming packets to a DumpFrameFilter

**Downloads:** {download}`Python <t01_mediafile_dump.py>` · {download}`C++ <t01_mediafile_dump.cpp>`

In this first tutorial we build the simplest possible Limef pipeline:

```{mermaid}
flowchart TD
    src[MediaFileTR]
    dump(DumpFF)

    src --- dump

    classDef thread fill:#4a90d9,stroke:#2c5f8a,color:#fff
    classDef ff     fill:#5ba85a,stroke:#3d6e3d,color:#fff
    class src thread
    class dump ff
```

{cpp:class}`Limef::thread::MediaFileThread` reads a media file and pushes encoded
{cpp:class}`Limef::frame::PacketFrame`s downstream.
{cpp:class}`Limef::ff::DumpFrameFilter` prints a one-line description of every
passing frame to stdout and passes it on.

We stream at the file's **natural playback speed** by setting `fps = -1`.

```python
import time
import sys
import limef
```

## Build the filterchain

First create the `DumpFrameFilter`, then connect the source thread to it.
Filters must be wired **before** `start()` is called.

```python
dump = limef.DumpFrameFilter("dump")
```

## Configure the source thread

{cpp:class}`Limef::thread::MediaFileContext` holds the parameters for the source thread.

Key options:

| Parameter | Value | Meaning |
|-----------|-------|---------|
| `fps` | `0` | feed as fast as possible (default) |
| `fps` | `-1` | feed at the stream's natural playback speed |
| `fps` | `N` | feed at N frames per second |
| `loop` | `-1` | do not loop (default) |
| `loop` | `0` | loop immediately at EOF |
| `loop` | `N` | pause N ms before restarting |

Here we use `fps = -1` so packets are paced to the stream's original timing.

```python
media_file = sys.argv[1] if len(sys.argv) > 1 else "video.mp4"

ctx      = limef.MediaFileContext(media_file, slot=1)
ctx.fps  = -1   # natural live speed
```

## Start and stop

Connect the thread to the filterchain with `cc()`, start it, wait, then stop.
`stop()` sends a stop signal through the pipeline and blocks until the thread exits.

```python
thread = limef.MediaFileThread("reader", ctx)
thread.cc(dump)
thread.start()

print("Streaming for 5 seconds — watch the DumpFrameFilter output ...")
try:
    time.sleep(5)
except KeyboardInterrupt:
    pass

thread.stop()
print("Done.")
```
