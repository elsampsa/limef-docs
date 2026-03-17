# Decoders

Decoders convert encoded {cpp:class}`Limef::frame::PacketFrame`s into
decoded {cpp:class}`Limef::frame::DecodedFrame`s.
The abstract interface is {cpp:class}`Limef::decode::Decoder`; the main
implementation is {cpp:class}`Limef::decode::FFmpegDecoder`.

```{eval-rst}
.. doxygennamespace:: Limef::decode
   :members:
```
