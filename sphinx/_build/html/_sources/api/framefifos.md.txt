# FrameFifos

A FrameFifo manages a pool of pre-allocated frames (stack) and a queue (fifo) for
inter-thread communication.  All `FrameFifo` variants live in the `Limef` namespace.

```{eval-rst}
.. doxygenclass:: Limef::FrameFifo
   :members:

.. doxygenclass:: Limef::OrderedFrameFifo
   :members:

.. doxygenclass:: Limef::DecodedFrameFifo
   :members:

.. doxygenclass:: Limef::TensorFrameFifo
   :members:

.. doxygenclass:: Limef::PollFrameFifo
   :members:
```
