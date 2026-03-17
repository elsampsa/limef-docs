# Under the Hood

*How threads, framefifos and frame memory work inside Limef*

## Thread boundaries

A filterchain ends at a **thread boundary** — the input framefilter of a consumer thread.
The producer calls `go()` synchronously on its filterchain; the consumer runs its own independent
loop.  They are decoupled by the {cpp:class}`Limef::FrameFifo`.

```{mermaid}
flowchart TD
    prod["ProducerThread"]
    ff["framefilters"]
    boundary["thread boundary"]
    fifo["FrameFifo"]
    cons["ConsumerThread"]

    prod --> ff --> boundary --> fifo --> cons
```

This means you never need explicit locking in application code when wiring two threads together.

## The FrameFifo: stack and fifo

Each consumer thread owns a {cpp:class}`Limef::FrameFifo` that manages two structures:

- **Stack** — a pool of pre-allocated frames (circular buffer)
- **Fifo** — a queue of frames ready for processing (`std::deque`)

When a frame arrives at the thread boundary:

```
1. pop a pre-allocated frame from the stack
2. copy the incoming frame into it
3. push the copy into the fifo
4. thread loop: read the frame from the fifo
5. run the internal filterchain with that frame
6. recycle the frame → return it to the stack
```

This avoids constant `malloc`/`free` for high-throughput types like
{cpp:class}`Limef::frame::PacketFrame` and {cpp:class}`Limef::frame::DecodedFrame`.

## Frame memory adaptation

Stack frames **adapt** to incoming data and **reuse** allocations:

```
First frame arrives (e.g., 1920×1080):
  → stack frame allocates buffer for 1920×1080
  → copies data
  → frame recycled, returns to stack WITH its buffer

Next frame arrives (same size):
  → buffer already fits, just copy — no reallocation

Larger frame arrives (e.g., 4K):
  → buffer too small, reallocate
  → copies data
```

### Key FrameFifo methods

| Method | Called by | Purpose |
|--------|-----------|---------|
| `writeCopy(frame)` | Input framefilter | Copy incoming frame into the fifo |
| `updateFrom(frame)` | FrameFifo internally | Copy data into a stack frame |
| `read(timeout)` | Consumer thread loop | Get next frame from the fifo |
| `recycle(frame)` | Consumer thread loop | Return frame to the stack |

Frame pointers from `read()` are **owned by the FrameFifo** — never `delete` them; always call `recycle()`.

## Thread templating

Threads are templated on a frame type: `Thread<T>`.  The template parameter `T` is the
"special" frame type that gets the stack/copy treatment described above.  All other frame types
(e.g. {cpp:class}`Limef::frame::SignalFrame`) pass through without pre-allocation.

**Producer threads** (e.g. {cpp:class}`Limef::thread::MediaFileThread`) don't use a FrameFifo —
they just produce frames and push them downstream.

**Consumer threads** own a `FrameFifo<T>` sized by a {cpp:class}`Limef::FrameFifoContext` passed at construction.

## SignalFrames and thread control

Thread control (start, stop, flush, parameter updates) travels through the same filterchain as media
frames, packaged as {cpp:class}`Limef::frame::SignalFrame`.  The thread backend dispatches them
inside its loop — same thread context as frame processing, no extra locking needed.

The signal return path (thread backend → main thread) uses {cpp:class}`Limef::signal::Signal`
objects read via {cpp:func}`Limef::thread::Thread::read`.

## Frame ownership rules in filterchains

```
upstream ──► framefilter ──► downstream
```

1. A framefilter **must not modify** a frame it received from upstream — take an internal copy first if modification is needed.
2. A framefilter may produce frames of a different type (e.g. consume `PacketFrame`, emit `DecodedFrame`).
3. Downstream frames may hold **pointers into** upstream frames as long as rule 1 is not violated — useful for zero-copy GPU memory paths.

## Memory style: objects not pointers

Inside the library, framefilters are plain stack-allocated objects chained by raw pointer:

```cpp
InfoFrameFilter     info("info");
DumpFrameFilter     dump("dump");
DecodingFrameFilter decode("decode");

info.cc(dump).cc(decode);
```

Application code is free to use smart pointers for heap allocation:

```cpp
auto dump   = std::make_shared<DumpFrameFilter>("dump");
auto decode = std::make_shared<DecodingFrameFilter>("decode");
decode->cc(*dump);
```

Python bindings use Python reference semantics — object lifetime is managed automatically.
