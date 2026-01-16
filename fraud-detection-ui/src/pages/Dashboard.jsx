import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import ModeSelector from '../components/ModeSelector';
import BankingForm from '../components/BankingForm';
import CreditCardForm from '../components/CreditCardForm';
import ResultDisplay from '../components/ResultDisplay';
import { checkFraud, submitFeedback, getStats } from '../services/api';

function Dashboard({ user }) {
  const [mode, setMode] = useState('banking');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showStats, setShowStats] = useState(false);
  const [stats, setStats] = useState(null);
  const [totalUsers, setTotalUsers] = useState(0);

  useEffect(() => {
    const users = JSON.parse(localStorage.getItem('registeredUsers') || '[]');
    setTotalUsers(users.length);
  }, []);

  const loadStats = async () => {
    try {
      const data = await getStats();
      setStats(data);
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  const handleShowStats = () => {
    setShowStats(!showStats);
    if (!showStats) {
      loadStats();
    }
  };

  const handleCheckFraud = async (formData) => {
    setLoading(true);
    setResult(null);

    try {
      if (mode === 'banking') {
        const timestamp = formData.Timestamp.replace('T', ' ') + ':00';
        formData = { ...formData, Timestamp: timestamp };
      }

      const data = await checkFraud(mode, formData);
      console.log('Fraud check result:', data);
      setResult(data);

      setTimeout(() => {
        window.scrollTo({
          top: document.documentElement.scrollHeight,
          behavior: 'smooth'
        });
      }, 100);

    } catch (error) {
      console.error('Error:', error);
      alert(' Error checking fraud. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleFeedback = async (predictionId, actualClass, note) => {
    try {
      console.log('Submitting feedback:', { predictionId, actualClass, note });
      await submitFeedback(predictionId, actualClass, note);
      alert(' Thank you for your feedback!');
      setResult(null);

      if (showStats) {
        loadStats();
      }
    } catch (error) {
      console.error('Error:', error);
      alert(' Error submitting feedback');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-950 via-purple-950 to-slate-950 relative overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {/* Neural Network Lines */}
        <svg className="absolute w-full h-full opacity-20">
          <defs>
            <linearGradient id="line-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#06b6d4" />
              <stop offset="100%" stopColor="#8b5cf6" />
            </linearGradient>
          </defs>
          {[...Array(20)].map((_, i) => (
            <line
              key={i}
              x1={`${Math.random() * 100}%`}
              y1={`${Math.random() * 100}%`}
              x2={`${Math.random() * 100}%`}
              y2={`${Math.random() * 100}%`}
              stroke="url(#line-gradient)"
              strokeWidth="1"
              className="animate-pulse"
              style={{ animationDelay: `${i * 0.2}s` }}
            />
          ))}
        </svg>

        {/* Glowing Orbs */}
        <div className="absolute top-20 left-20 w-64 h-64 bg-cyan-500 rounded-full filter blur-3xl opacity-20 animate-pulse"></div>
        <div className="absolute bottom-20 right-20 w-96 h-96 bg-purple-500 rounded-full filter blur-3xl opacity-20 animate-pulse" style={{ animationDelay: '1s' }}></div>
        <div className="absolute top-1/2 left-1/2 w-80 h-80 bg-pink-500 rounded-full filter blur-3xl opacity-10 animate-pulse" style={{ animationDelay: '2s' }}></div>
      </div>

      <Navbar user={user} />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 relative z-10">
        <div className="mb-12">
          <div className="flex justify-between items-center flex-wrap gap-4">
            <div>
              <h1 className="text-5xl font-extrabold bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-400 bg-clip-text text-transparent mb-3 drop-shadow-lg">
                Fraud Detection Dashboard
              </h1>
              <p className="text-xl text-cyan-300 font-medium flex items-center space-x-2">
                <span className="text-purple-400">Neural Warden:</span>
                <span>AI-powered fraud detection</span>
              </p>
            </div>
            <button
              onClick={handleShowStats}
              className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-8 py-4 rounded-2xl font-bold hover:from-purple-700 hover:to-pink-700 transition-all duration-200 shadow-lg hover:shadow-purple-500/50 transform hover:scale-105 border border-purple-400/30"
            >
              {showStats ? '📊 Hide Stats' : '📊 Show Stats'}
            </button>
          </div>
        </div>

        {showStats && stats && (
          <div className="mb-8 animate-fadeIn">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-gradient-to-br from-blue-600/20 to-blue-800/20 backdrop-blur-md border border-blue-400/30 text-white p-8 rounded-3xl shadow-xl hover:shadow-blue-500/50 transition-all duration-300 transform hover:scale-105">
                <p className="text-blue-300 text-sm font-semibold mb-2">Total Predictions</p>
                <p className="text-5xl font-black mb-2">
                  {stats.total_predictions?.toLocaleString() || 0}
                </p>
              </div>

              <div className="bg-gradient-to-br from-green-600/20 to-green-800/20 backdrop-blur-md border border-green-400/30 text-white p-8 rounded-3xl shadow-xl hover:shadow-green-500/50 transition-all duration-300 transform hover:scale-105">
                <p className="text-green-300 text-sm font-semibold mb-2">With Feedback</p>
                <p className="text-5xl font-black mb-2">
                  {stats.with_feedback?.toLocaleString() || 0}
                </p>
              </div>

              <div className="bg-gradient-to-br from-purple-600/20 to-purple-800/20 backdrop-blur-md border border-purple-400/30 text-white p-8 rounded-3xl shadow-xl hover:shadow-purple-500/50 transition-all duration-300 transform hover:scale-105">
                <p className="text-purple-300 text-sm font-semibold mb-2">Feedback Rate</p>
                <p className="text-5xl font-black mb-2">
                  {stats.feedback_rate || 0}%
                </p>
              </div>

              <div className="bg-gradient-to-br from-orange-600/20 to-orange-800/20 backdrop-blur-md border border-orange-400/30 text-white p-8 rounded-3xl shadow-xl hover:shadow-orange-500/50 transition-all duration-300 transform hover:scale-105">
                <p className="text-orange-300 text-sm font-semibold mb-2">Active Users</p>
                <p className="text-5xl font-black mb-2">
                  {totalUsers.toLocaleString()}
                </p>
              </div>
            </div>
          </div>
        )}

        <ModeSelector mode={mode} setMode={setMode} />

        {mode === 'banking' ? (
          <BankingForm onSubmit={handleCheckFraud} loading={loading} />
        ) : (
          <CreditCardForm onSubmit={handleCheckFraud} loading={loading} />
        )}

        <ResultDisplay result={result} onFeedback={handleFeedback} />
      </div>

      <style jsx>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .animate-fadeIn {
          animation: fadeIn 0.5s ease-out;
        }
      `}</style>
    </div>
  );
}

export default Dashboard;