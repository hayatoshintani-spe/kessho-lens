export interface RecorderHandle {
  start: () => Promise<void>;
  stop: () => Promise<Blob>;
  state: () => "idle" | "recording" | "stopped";
}

export function createRecorder(): RecorderHandle {
  let mediaRecorder: MediaRecorder | null = null;
  let chunks: BlobPart[] = [];
  let state: "idle" | "recording" | "stopped" = "idle";
  let stream: MediaStream | null = null;

  return {
    async start() {
      if (typeof window === "undefined") return;
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mime =
        MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
          ? "audio/webm;codecs=opus"
          : MediaRecorder.isTypeSupported("audio/webm")
          ? "audio/webm"
          : "";
      mediaRecorder = mime
        ? new MediaRecorder(stream, { mimeType: mime })
        : new MediaRecorder(stream);
      chunks = [];
      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunks.push(e.data);
      };
      mediaRecorder.start();
      state = "recording";
    },
    stop() {
      return new Promise<Blob>((resolve) => {
        if (!mediaRecorder) {
          state = "stopped";
          resolve(new Blob());
          return;
        }
        mediaRecorder.onstop = () => {
          const blob = new Blob(chunks, {
            type: mediaRecorder?.mimeType || "audio/webm",
          });
          stream?.getTracks().forEach((t) => t.stop());
          state = "stopped";
          resolve(blob);
        };
        mediaRecorder.stop();
      });
    },
    state: () => state,
  };
}
