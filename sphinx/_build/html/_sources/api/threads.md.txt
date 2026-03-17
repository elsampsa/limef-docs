# Threads

Threads are the active components of a pipeline.  The base class
{cpp:class}`Limef::thread::Thread` is templated on the frame type it handles specially.
Each thread exposes {cpp:func}`Limef::thread::Thread::getInput` and
{cpp:func}`Limef::thread::Thread::getOutput` as connection points.

```{eval-rst}
.. doxygennamespace:: Limef::thread
   :members:
```
