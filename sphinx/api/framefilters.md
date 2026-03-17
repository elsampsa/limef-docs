# Framefilters

Framefilters are the building blocks of pipelines.
The base class {cpp:class}`Limef::ff::FrameFilter` defines the `go()` / `cc()` / `pass()` interface.
Use {cpp:class}`Limef::ff::SimpleFrameFilter` for one-to-one filters and
{cpp:class}`Limef::ff::SplitFrameFilter` for one-to-many forks.

```{eval-rst}
.. doxygennamespace:: Limef::ff
   :members:
```
