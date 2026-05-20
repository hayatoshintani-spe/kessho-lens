"use client";

import { useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Mic, Square, Trash2 } from "lucide-react";
import { createRecorder, type RecorderHandle } from "@/lib/audio/recorder";

interface Props {
  onRecorded?: (blob: Blob) => void;
}

export function AudioRecorder({ onRecorded }: Props) {
  const recorderRef = useRef<RecorderHandle | null>(null);
  const [recording, setRecording] = useState(false);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [blob, setBlob] = useState<Blob | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function start() {
    setError(null);
    try {
      const r = createRecorder();
      recorderRef.current = r;
      await r.start();
      setRecording(true);
    } catch (err) {
      setError("マイクへのアクセスが拒否されました");
      setRecording(false);
    }
  }

  async function stop() {
    if (!recorderRef.current) return;
    const b = await recorderRef.current.stop();
    setBlob(b);
    setAudioUrl(URL.createObjectURL(b));
    setRecording(false);
    onRecorded?.(b);
  }

  function reset() {
    if (audioUrl) URL.revokeObjectURL(audioUrl);
    setAudioUrl(null);
    setBlob(null);
  }

  return (
    <div className="rounded-md border bg-white p-3">
      <div className="flex items-center gap-2">
        {recording ? (
          <Button variant="destructive" size="sm" onClick={stop}>
            <Square className="h-4 w-4" />
            停止
          </Button>
        ) : (
          <Button size="sm" onClick={start}>
            <Mic className="h-4 w-4" />
            録音
          </Button>
        )}
        {audioUrl && !recording && (
          <Button variant="ghost" size="sm" onClick={reset}>
            <Trash2 className="h-4 w-4" />
            破棄
          </Button>
        )}
        {recording && (
          <span className="ml-2 flex items-center gap-2 text-sm text-red-600">
            <span className="inline-block h-2 w-2 animate-pulse rounded-full bg-red-500" />
            録音中…
          </span>
        )}
      </div>
      {audioUrl && (
        <audio className="mt-3 w-full" controls src={audioUrl}>
          お使いのブラウザは audio タグをサポートしていません。
        </audio>
      )}
      {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
      {blob && (
        <p className="mt-2 text-xs text-slate-500">
          サイズ: {(blob.size / 1024).toFixed(1)} KB ・ 形式: {blob.type || "audio"}
        </p>
      )}
    </div>
  );
}
