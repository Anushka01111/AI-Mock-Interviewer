import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import apiClient from '../api/client';

export default function Report() {
  const { sessionId } = useParams();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    async function fetchReport() {
      try {
        const res = await apiClient.get(`/sessions/${sessionId}/report`);
        if (res.data.error) {
          setError(res.data.error);
        } else {
          setReport(res.data);
        }
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to load report.');
      } finally {
        setLoading(false);
      }
    }
    fetchReport();
  }, [sessionId]);

  const downloadPdf = async () => {
    setDownloading(true);
    try {
      // Use apiClient so the Authorization header is attached automatically,
      // and request the response as a raw file (blob) instead of JSON.
      const res = await apiClient.get(`/sessions/${sessionId}/report/pdf`, {
        responseType: 'blob',
      });

      // Turn the blob into a temporary downloadable link and click it
      const url = window.URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `interview_report_session_${sessionId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError('Failed to download PDF. Please try again.');
    } finally {
      setDownloading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <p className="text-slate-400">Generating your feedback report...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center px-4">
        <div className="text-center max-w-md">
          <p className="text-red-400 mb-4">{error}</p>
          <Link to="/dashboard" className="text-indigo-400 hover:text-indigo-300">
            Back to dashboard
          </Link>
        </div>
      </div>
    );
  }

  const ScoreCard = ({ title, data }) => (
    <div className="bg-slate-800/60 border border-slate-700/50 rounded-2xl p-6">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-white font-semibold">{title}</h3>
        <span className="text-2xl font-bold text-indigo-400">
          {data.score_out_of_10}<span className="text-sm text-slate-500">/10</span>
        </span>
      </div>
      <p className="text-slate-300 text-sm leading-relaxed">{data.summary}</p>
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur">
        <div className="max-w-4xl mx-auto px-6 py-4 flex items-center justify-between">
          <span className="text-white font-semibold">AI Mock Interviewer</span>
          <Link to="/dashboard" className="text-sm text-slate-400 hover:text-white transition">
            New interview
          </Link>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-12">
        <div className="mb-8">
          <h1 className="text-2xl font-semibold text-white mb-2">Your interview report</h1>
          <p className="text-slate-400">Here's how you performed across all three dimensions.</p>
        </div>

        <div className="grid gap-4 mb-6">
          <ScoreCard title="Communication" data={report.communication} />
          <ScoreCard title="Answer Quality" data={report.answer_quality} />
          <ScoreCard title="Body Language" data={report.body_language} />
        </div>

        <div className="bg-slate-800/60 border border-slate-700/50 rounded-2xl p-6 mb-6">
          <h3 className="text-white font-semibold mb-2">Overall trend</h3>
          <p className="text-slate-300 text-sm leading-relaxed">{report.overall_trend}</p>
        </div>

        <div className="bg-slate-800/60 border border-slate-700/50 rounded-2xl p-6 mb-8">
          <h3 className="text-white font-semibold mb-4">Action plan</h3>
          <ul className="space-y-3">
            {report.action_plan.map((item, i) => (
              <li key={i} className="flex items-start gap-3 text-sm text-slate-300">
                <span className="flex-shrink-0 w-5 h-5 rounded-full bg-emerald-500/10 text-emerald-400 text-xs flex items-center justify-center mt-0.5">
                  {i + 1}
                </span>
                {item}
              </li>
            ))}
          </ul>
        </div>

        {error && (
          <div className="bg-red-500/10 border border-red-500/30 text-red-400 text-sm rounded-lg px-4 py-2.5 mb-4">
            {error}
          </div>
        )}

        <button
          onClick={downloadPdf}
          disabled={downloading}
          className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-800 disabled:cursor-not-allowed text-white font-medium py-3 rounded-lg transition shadow-lg shadow-indigo-600/20"
        >
          {downloading ? 'Preparing your PDF...' : 'Download PDF report'}
        </button>
      </main>
    </div>
  );
}
