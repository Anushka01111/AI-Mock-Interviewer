import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '../api/client';

export default function Dashboard() {
  const [candidateName, setCandidateName] = useState('');
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [questions, setQuestions] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    navigate('/login');
  };

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!file) {
      setError('Please select a resume PDF first.');
      return;
    }

    setLoading(true);

    try {
      // Step 1: Create a session
      const sessionRes = await apiClient.post('/sessions/', {
        candidate_name: candidateName || 'Candidate',
      });
      const newSessionId = sessionRes.data.session_id;
      setSessionId(newSessionId);

      // Step 2: Upload resume to that session
      const formData = new FormData();
      formData.append('file', file);

      const uploadRes = await apiClient.post(
        `/sessions/${newSessionId}/upload-resume`,
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );

      setQuestions(uploadRes.data);
    } catch (err) {
      setError(
        err.response?.data?.detail || 'Something went wrong. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  const startInterview = () => {
    navigate(`/interview/${sessionId}`, { state: { questions } });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur">
        <div className="max-w-4xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center">
              <svg className="w-5 h-5 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
            </div>
            <span className="text-white font-semibold">AI Mock Interviewer</span>
          </div>
          <button
            onClick={handleLogout}
            className="text-sm text-slate-400 hover:text-white transition"
          >
            Sign out
          </button>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-12">
        {!questions ? (
          <>
            <div className="mb-8">
              <h1 className="text-2xl font-semibold text-white mb-2">
                Start a new mock interview
              </h1>
              <p className="text-slate-400">
                Upload your resume and we'll generate personalised interview questions based on your experience.
              </p>
            </div>

            <div className="bg-slate-800/60 backdrop-blur border border-slate-700/50 rounded-2xl p-8">
              <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1.5">
                    Your name
                  </label>
                  <input
                    type="text"
                    value={candidateName}
                    onChange={(e) => setCandidateName(e.target.value)}
                    placeholder="Enter your name"
                    className="w-full bg-slate-900/50 border border-slate-700 rounded-lg px-4 py-2.5 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1.5">
                    Resume (PDF)
                  </label>
                  <div className="relative">
                    <input
                      type="file"
                      accept="application/pdf"
                      onChange={handleFileChange}
                      className="w-full text-sm text-slate-400 bg-slate-900/50 border border-slate-700 border-dashed rounded-lg px-4 py-6 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-indigo-600 file:text-white hover:file:bg-indigo-500 file:cursor-pointer cursor-pointer transition"
                    />
                  </div>
                  {file && (
                    <p className="text-sm text-emerald-400 mt-2">✓ {file.name}</p>
                  )}
                </div>

                {error && (
                  <div className="bg-red-500/10 border border-red-500/30 text-red-400 text-sm rounded-lg px-4 py-2.5">
                    {error}
                  </div>
                )}

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-800 disabled:cursor-not-allowed text-white font-medium py-3 rounded-lg transition shadow-lg shadow-indigo-600/20"
                >
                  {loading ? 'Analysing resume & generating questions...' : 'Generate interview questions'}
                </button>
              </form>
            </div>
          </>
        ) : (
          <>
            <div className="mb-8 text-center">
              <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 mb-4">
                <svg className="w-7 h-7 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h1 className="text-2xl font-semibold text-white mb-2">
                Your interview is ready
              </h1>
              <p className="text-slate-400">
                We generated {questions.length} personalised questions based on your resume.
              </p>
            </div>

            {/* What to expect */}
            <div className="bg-slate-800/60 border border-slate-700/50 rounded-2xl p-8 mb-6">
              <h2 className="text-white font-semibold mb-5">How this works</h2>

              <div className="space-y-5">
                <div className="flex gap-4">
                  <div className="flex-shrink-0 w-9 h-9 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 text-sm font-semibold">
                    1
                  </div>
                  <div>
                    <p className="text-white text-sm font-medium mb-0.5">One question at a time</p>
                    <p className="text-slate-400 text-sm">
                      You'll see each question only when it's time to answer it — questions are scaled from easy to hard, so treat it like a real interview.
                    </p>
                  </div>
                </div>

                <div className="flex gap-4">
                  <div className="flex-shrink-0 w-9 h-9 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 text-sm font-semibold">
                    2
                  </div>
                  <div>
                    <p className="text-white text-sm font-medium mb-0.5">Camera & microphone</p>
                    <p className="text-slate-400 text-sm">
                      Your browser will ask for camera and mic access. Make sure you're in a quiet, well-lit space and speak clearly.
                    </p>
                  </div>
                </div>

                <div className="flex gap-4">
                  <div className="flex-shrink-0 w-9 h-9 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 text-sm font-semibold">
                    3
                  </div>
                  <div>
                    <p className="text-white text-sm font-medium mb-0.5">Record, review, submit</p>
                    <p className="text-slate-400 text-sm">
                      Hit record, answer naturally, then stop. You can re-record before submitting if you're not happy with a take.
                    </p>
                  </div>
                </div>
              </div>

              <div className="h-px bg-slate-700/50 my-6" />

              <h2 className="text-white font-semibold mb-5">What you're evaluated on</h2>

              <div className="grid sm:grid-cols-3 gap-4">
                <div className="bg-slate-900/40 rounded-xl p-4">
                  <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center mb-3">
                    <svg className="w-4 h-4 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <p className="text-white text-sm font-medium mb-1">Answer accuracy</p>
                  <p className="text-slate-400 text-xs leading-relaxed">
                    How relevant and correct your answers are, compared against ideal responses.
                  </p>
                </div>

                <div className="bg-slate-900/40 rounded-xl p-4">
                  <div className="w-8 h-8 rounded-lg bg-purple-500/10 flex items-center justify-center mb-3">
                    <svg className="w-4 h-4 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 003-3V5a3 3 0 00-6 0v6a3 3 0 003 3z" />
                    </svg>
                  </div>
                  <p className="text-white text-sm font-medium mb-1">Speech & clarity</p>
                  <p className="text-slate-400 text-xs leading-relaxed">
                    Your pace, confidence, and clarity while speaking — not just what you say, but how.
                  </p>
                </div>

                <div className="bg-slate-900/40 rounded-xl p-4">
                  <div className="w-8 h-8 rounded-lg bg-emerald-500/10 flex items-center justify-center mb-3">
                    <svg className="w-4 h-4 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  </div>
                  <p className="text-white text-sm font-medium mb-1">Body language</p>
                  <p className="text-slate-400 text-xs leading-relaxed">
                    Eye contact, facial engagement, and head posture during your answers.
                  </p>
                </div>
              </div>
            </div>

            <button
              onClick={startInterview}
              className="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-medium py-3 rounded-lg transition shadow-lg shadow-emerald-600/20"
            >
              Begin interview →
            </button>
          </>
        )}
      </main>
    </div>
  );
}
