# Encoders

Encoders convert decoded {cpp:class}`Limef::frame::DecodedFrame`s into
encoded {cpp:class}`Limef::frame::PacketFrame`s.
The abstract interface is {cpp:class}`Limef::encode::Encoder`; the main
implementation is {cpp:class}`Limef::encode::FFmpegEncoder`.

```{eval-rst}
.. doxygennamespace:: Limef::encode
   :members:
```
