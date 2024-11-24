export class Player {
  private playbackNode: AudioWorkletNode | null = null;

  async init(sampleRate: number) {
    const audioContext = new AudioContext({ sampleRate });
    await audioContext.audioWorklet.addModule("playback-worklet.js");

    this.playbackNode = new AudioWorkletNode(audioContext, "playback-worklet");
    this.playbackNode.connect(audioContext.destination);
  }

  play(buffer: Int16Array) {
    if (this.playbackNode) {
      this.playbackNode.port.postMessage(buffer);
    }
  }

  clear() {
    if (this.playbackNode) {
      this.playbackNode.port.postMessage(null);
    }
  }
}

export class Recorder {
  onDataAvailable: (buffer: ArrayBuffer) => void;
  private audioContext: AudioContext | null = null;
  private mediaStream: MediaStream | null = null;
  private mediaStreamSource: MediaStreamAudioSourceNode | null = null;
  private workletNode: AudioWorkletNode | null = null;

  public constructor(onDataAvailable: (buffer: ArrayBuffer) => void) {
    this.onDataAvailable = onDataAvailable;
  }

  async start(stream: MediaStream) {
    try {
      this.audioContext = new AudioContext({ sampleRate: 24000 });
      await this.audioContext.audioWorklet.addModule(
        "./audio-worklet-processor.js"
      );
      this.mediaStream = stream;
      this.mediaStreamSource = this.audioContext.createMediaStreamSource(
        this.mediaStream
      );
      this.workletNode = new AudioWorkletNode(
        this.audioContext,
        "audio-worklet-processor"
      );
      let buffer: Uint8Array[] = [];
      let bufferSize = 0;
      const targetSize = 4800;
      this.workletNode.port.onmessage = (event) => {
        const data = new Uint8Array(event.data.buffer);
        buffer.push(data);
        bufferSize += data.byteLength;

        if (bufferSize >= targetSize) {
          const concatenatedBuffer = new Uint8Array(bufferSize);
          let offset = 0;
          for (const chunk of buffer) {
            concatenatedBuffer.set(chunk, offset);
            offset += chunk.byteLength;
          }
          this.onDataAvailable(concatenatedBuffer.buffer);
          buffer = [];
          bufferSize = 0;
        }
      };
      this.mediaStreamSource.connect(this.workletNode);
      this.workletNode.connect(this.audioContext.destination);
    } catch (error) {
      this.stop();
    }
  }

  stop() {
    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach((track) => track.stop());
    }
    if (this.audioContext) {
      this.audioContext.close();
    }
  }
}

