/**
 * MobileDailyLog — simplified daily log form for one-thumb use.
 * Supports voice-to-text via Web Speech API and offline draft saving.
 */
import { useState, useRef } from 'react';
import { offlineDb } from '@/services/offlineDb';
import { apiClient } from '@/api/client';

type Props = {
  projectId: string;
  logDate: string; // YYYY-MM-DD
  onSubmit?: () => void;
};

type SpeechRecognition = {
  lang: string;
  continuous: boolean;
  interimResults: boolean;
  onresult: ((event: { results: { [key: number]: { [key: number]: { transcript: string } } } }) => void) | null;
  onerror: ((event: { error: string }) => void) | null;
  start: () => void;
  stop: () => void;
};

declare global {
  interface Window {
    SpeechRecognition: new () => SpeechRecognition;
    webkitSpeechRecognition: new () => SpeechRecognition;
  }
}

export const MobileDailyLog = ({ projectId, logDate, onSubmit }: Props) => {
  const [notes, setNotes] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [status, setStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle');
  const recognitionRef = useRef<SpeechRecognition | null>(null);

  const hasSpeechRecognition =
    typeof window !== 'undefined' &&
    ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window);

  const toggleVoice = () => {
    if (!hasSpeechRecognition) return;
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (isListening) {
      recognitionRef.current?.stop();
      setIsListening(false);
      return;
    }

    const recognition = new SR();
    recognition.lang = 'en-US';
    recognition.continuous = true;
    recognition.interimResults = false;
    recognition.onresult = (event) => {
      const transcript = Object.values(event.results)
        .map((r) => r[0].transcript)
        .join(' ');
      setNotes((prev) => (prev ? prev + ' ' + transcript : transcript));
    };
    recognition.onerror = () => setIsListening(false);
    recognition.start();
    recognitionRef.current = recognition;
    setIsListening(true);
  };

  const handleSaveDraft = async () => {
    const id = `daily_log_${projectId}_${logDate}`;
    await offlineDb.saveDailyLogDraft({
      id,
      projectId,
      logDate,
      notes,
      updatedAt: new Date().toISOString(),
    });
    setStatus('saved');
    setTimeout(() => setStatus('idle'), 2000);
  };

  const handleSubmit = async () => {
    setStatus('saving');
    try {
      if (navigator.onLine) {
        await apiClient.post('/api/v1/field-ops/daily-logs/', {
          project: projectId,
          log_date: logDate,
          notes,
        });
        onSubmit?.();
        setStatus('saved');
      } else {
        await handleSaveDraft();
      }
    } catch {
      setStatus('error');
    }
  };

  return (
    <div className="flex flex-col gap-4 p-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-slate-900">Daily Log</h2>
        <span className="text-sm text-slate-500">{logDate}</span>
      </div>

      <div className="relative">
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="What happened on site today? (or use voice)"
          rows={6}
          className="w-full rounded-xl border border-slate-200 p-4 pr-12 text-base text-slate-900 placeholder-slate-400 focus:border-amber-400 focus:outline-none focus:ring-2 focus:ring-amber-200"
        />
        {hasSpeechRecognition && (
          <button
            type="button"
            onClick={toggleVoice}
            aria-label={isListening ? 'Stop voice input' : 'Start voice input'}
            className={[
              'absolute right-3 top-3 rounded-full p-2 transition-colors',
              isListening
                ? 'bg-red-100 text-red-600 animate-pulse'
                : 'bg-slate-100 text-slate-500 hover:bg-slate-200',
            ].join(' ')}
          >
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round"
                d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 016 0v6a3 3 0 01-3 3z" />
            </svg>
          </button>
        )}
      </div>

      {status === 'error' && (
        <p className="text-sm text-red-600">Failed to submit. Draft saved locally.</p>
      )}
      {status === 'saved' && (
        <p className="text-sm text-green-600">Saved successfully.</p>
      )}

      <div className="flex gap-3">
        <button
          type="button"
          onClick={handleSaveDraft}
          className="flex-1 rounded-xl border border-slate-300 py-3 text-sm font-medium text-slate-700 hover:bg-slate-50"
        >
          Save Draft
        </button>
        <button
          type="button"
          onClick={handleSubmit}
          disabled={status === 'saving' || !notes.trim()}
          className="flex-1 rounded-xl bg-amber-500 py-3 text-sm font-medium text-white hover:bg-amber-600 disabled:opacity-50"
        >
          {status === 'saving' ? 'Submitting…' : navigator.onLine ? 'Submit' : 'Queue Offline'}
        </button>
      </div>
    </div>
  );
};
