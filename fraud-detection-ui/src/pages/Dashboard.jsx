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
      alert('❌ Error checking fraud. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleFeedback = async (predictionId, actualClass, note) => {
    try {
      console.log('Submitting feedback:', { predictionId, actualClass, note });
      await submitFeedback(predictionId, actualClass, note);
      alert('✅ Thank you for your feedback!');
      setResult(null);
      
      if (showStats) {
        loadStats();
      }
    } catch (error) {
      console.error('Error:', error);
      alert('❌ Error submitting feedback');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-purple-50 to-pink-50">
      <Navbar user={user} />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="mb-12">
          <div className="flex justify-between items-center flex-wrap gap-4">
            <div>
              <h1 className="text-5xl font-extrabold bg-gradient-to-r from-purple-600 via-pink-600 to-red-600 bg-clip-text text-transparent mb-3">
                Fraud Detection Dashboard
              </h1>
              <p className="text-xl text-gray-600 font-medium flex items-center space-x-2">
                <span>🤖</span>
                <span>AI-powered fraud detection</span>
              </p>
            </div>
            <button
              onClick={handleShowStats}
              className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-8 py-4 rounded-2xl font-bold hover:from-purple-700 hover:to-pink-700 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105"
            >
              {showStats ? '📊 Hide Stats' : '📊 Show Stats'}
            </button>
          </div>
        </div>

        {showStats && stats && (
          <div className="mb-8 animate-fadeIn">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white p-8 rounded-3xl shadow-xl">
                <p className="text-blue-100 text-sm font-semibold mb-2">Total Predictions</p>
                <p className="text-5xl font-black mb-2">
                  {stats.total_predictions?.toLocaleString() || 0}
                </p>
              </div>

              <div className="bg-gradient-to-br from-green-500 to-green-600 text-white p-8 rounded-3xl shadow-xl">
                <p className="text-green-100 text-sm font-semibold mb-2">With Feedback</p>
                <p className="text-5xl font-black mb-2">
                  {stats.with_feedback?.toLocaleString() || 0}
                </p>
              </div>

              <div className="bg-gradient-to-br from-purple-500 to-purple-600 text-white p-8 rounded-3xl shadow-xl">
                <p className="text-purple-100 text-sm font-semibold mb-2">Feedback Rate</p>
                <p className="text-5xl font-black mb-2">
                  {stats.feedback_rate || 0}%
                </p>
              </div>

              <div className="bg-gradient-to-br from-orange-500 to-orange-600 text-white p-8 rounded-3xl shadow-xl">
                <p className="text-orange-100 text-sm font-semibold mb-2">Active Users</p>
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
    </div>
  );
}

export default Dashboard;