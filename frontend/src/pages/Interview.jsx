import { useState, useRef, useEffect } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import apiClient from '../api/client';

export default function Interview() {
  const { sessionId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const questions = location.state?.questions || [];

  const [currentIndex, setCurrentIndex] = useState(0);
  const [isRecording, setIsRecording] = useState(false);
  const [hasRecorded, setHasRecorded] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [permissionError, setPermissionError] = useState('');
  const [answeredCount, setAnsweredCount] = useState(0);

  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const videoChunksRef = useRef([]);
  const audioRecorderRef = useRef(null);
  const videoBlobRef = useRef(null);
  const audioBlobRef = useRef(null);

  const currentQuestion = questions[currentIndex];
  const isLastQuestion = currentIndex === questions.length - 1;

  // Set up camera + mic preview when component mounts
  useEffect(() => {
    async function setupMedia() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: true,
        });
        streamRef.current = stream;
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      } catch (err) {
        setPermissionError(
          'Camera and microphone access is required for the interview. Please allow access and refresh the page.'
        );
      }
    }
    setupMedia();

    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
      }
    };
  }, []);

  const startRecording = () => {
    if (!streamRef.current) return;
    setError('');
    setHasRecorded(false);
    videoBlobRef.current = null;
    audioBlobRef.current = null;

    const stream = streamRef.current;

    // Record video (full stream, includes audio track too, but we separate below)
    videoChunksRef.current = [];
    const videoRecorder = new MediaRecorder(stream, { mimeType: 'video/webm' });
    videoRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) videoChunksRef.current.push(e.data);
    };
    videoRecorder.onstop = () => {
      videoBlobRef.current = new Blob(videoChunksRef.current, { type: 'video/webm' });
    };
    mediaRecorderRef.current = videoRecorder;

    // Record audio separately (audio-only track) for the speech pipeline
    const audioStream = new MediaStream(stream.getAudioTracks());
    audioChunksRef.current = [];
    const audioRecorder = new MediaRecorder(audioStream, { mimeType: 'audio/webm' });
    audioRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) audioChunksRef.current.push(e.data);
    };
    audioRecorder.onstop = () => {
      audioBlobRef.current = new Blob(audioChunksRef.current, { type: 'audio/webm' });
    };
    audioRecorderRef.current = audioRecorder;

    videoRecorder.start();
    audioRecorder.start();
    setIsRecording(true);
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current) mediaRecorderRef.current.stop();
    if (audioRecorderRef.current) audioRecorderRef.current.stop();
    setIsRecording(false);
    // Give a moment for onstop handlers to finish creating blobs
    setTimeout(() => setHasRecorded(true), 300);
  };

  const submitAnswer = async () => {
    if (!videoBlobRef.current || !audioBlobRef.current) {
      setError('Recording not ready yet, please wait a moment and try again.');
      return;
    }

    setSubmitting(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('question_id', currentQuestion.question_id);
      formData.append('audio_file', audioBlobRef.current, 'answer.webm');
      formData.append('video_file', videoBlobRef.current, 'answer.webm');

      await apiClient.post('/answers/submit-with-media', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      setAnsweredCount((c) => c + 1);

      if (isLastQuestion) {
        navigate(`/report/${sessionId}`);
      } else {
        setCurrentIndex((i) => i + 1);
        setHasRecorded(false);
      }
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          'Failed to submit your answer. Please try again.'
      );
    } finally {
      setSubmitting(false);
    }
  };

  const reRecord = () => {
    setHasRecorded(false);
    setError('');
  };

  if (permissionError) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center px-4">
        <div className="max-w-md text-center">
          <div className="text-5xl mb-4">🎥</div>
          <h2 className="text-xl font-semibold text-white mb-2">Camera access needed</h2>
          <p className="text-slate-400">{permissionError}</p>
        </div>
      </div>
    );
  }

  if (!questions.length) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center px-4">
        <div className="text-center">
          <p className="text-slate-400">No questions found. Please start a new session from the dashboard.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur">
        <div className="max-w-3xl mx-auto px-6 py-4 flex items-center justify-between">
          <span className="text-white font-semibold">AI Mock Interviewer</span>
          <span className="text-sm text-slate-400">
            Question {currentIndex + 1} of {questions.length}
          </span>
        </div>
        {/* Progress bar */}
        <div className="h-1 bg-slate-800">
          <div
            className="h-full bg-indigo-500 transition-all duration-500"
            style={{ width: `${((currentIndex) / questions.length) * 100}%` }}
          />
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-6 py-10">
        {/* Question */}
        <div className="bg-slate-800/60 border border-slate-700/50 rounded-2xl px-6 py-5 mb-6">
          <p className="text-xs font-medium text-indigo-400 uppercase tracking-wide mb-2">
            Question {currentIndex + 1}
          </p>
          <p className="text-lg text-white font-medium leading-relaxed">
            {currentQuestion.question_text}
          </p>
        </div>

        {/* Video preview */}
        <div className="relative bg-black rounded-2xl overflow-hidden mb-6 aspect-video">
          <video
            ref={videoRef}
            autoPlay
            muted
            playsInline
            className="w-full h-full object-cover"
          />
          {isRecording && (
            <div className="absolute top-4 left-4 flex items-center gap-2 bg-red-500/90 text-white text-sm font-medium px-3 py-1.5 rounded-full">
              <span className="w-2 h-2 bg-white rounded-full animate-pulse" />
              Recording
            </div>
          )}
        </div>

        {error && (
          <div className="bg-red-500/10 border border-red-500/30 text-red-400 text-sm rounded-lg px-4 py-2.5 mb-6">
            {error}
          </div>
        )}

        {/* Controls */}
        <div className="flex gap-3">
          {!isRecording && !hasRecorded && (
            <button
              onClick={startRecording}
              className="flex-1 bg-red-600 hover:bg-red-500 text-white font-medium py-3 rounded-lg transition shadow-lg shadow-red-600/20 flex items-center justify-center gap-2"
            >
              <span className="w-2.5 h-2.5 bg-white rounded-full" />
              Start recording answer
            </button>
          )}

          {isRecording && (
            <button
              onClick={stopRecording}
              className="flex-1 bg-slate-700 hover:bg-slate-600 text-white font-medium py-3 rounded-lg transition"
            >
              Stop recording
            </button>
          )}

          {hasRecorded && !isRecording && (
            <>
              <button
                onClick={reRecord}
                disabled={submitting}
                className="flex-1 bg-slate-700 hover:bg-slate-600 disabled:opacity-50 text-white font-medium py-3 rounded-lg transition"
              >
                Re-record
              </button>
              <button
                onClick={submitAnswer}
                disabled={submitting}
                className="flex-1 bg-emerald-600 hover:bg-emerald-500 disabled:bg-emerald-800 text-white font-medium py-3 rounded-lg transition shadow-lg shadow-emerald-600/20"
              >
                {submitting
                  ? 'Analysing your answer...'
                  : isLastQuestion
                  ? 'Submit & finish interview'
                  : 'Submit & next question'}
              </button>
            </>
          )}
        </div>
      </main>
    </div>
  );
}
