# GPU pipelines

"Uploading" frames to GPU

- `DecodingFrameFilter`, when initialized with hw decoding context, produces hw frames
- A thread using `DecodedFrameFifo` with target framefifo context set to gpu: `DecodedFrame`s given to such thread will turned into GPU frames
- Using `UploadGPUFrameFilter` 

"Downloading" frames to CPU

- `EncodingFrameFilter` when initialized hw encoding context and when fed `DecodedFrame`s that are on the GPU -> produces `PacketFrame`s on the CPU

