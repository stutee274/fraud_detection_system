import React, { useState } from 'react';

function ResultDisplay({ result, onFeedback }) {
  const [showFeedbackModal, setShowFeedbackModal] = useState(false);
  const [feedbackType, setFeedbackType] = useState(null);
  const [feedbackNote, setFeedbackNote] = useState('');

  if (!result) return null;

  const isFraud = result.prediction === 1;
  const prob = result.fraud_probability !== undefined ? result.fraud_probability : result.probability;
  const confidence = (prob * 100).toFixed(2);
  const predictionId = result.prediction_id;

  if (!predictionId) {
    console.warn(' Missing prediction_id - feedback disabled');
  }

  const handleFeedbackClick = (isCorrect) => {
    if (!predictionId) {
      alert('Cannot submit feedback: Database not connected');
      return;
    }

    const actualClass = isCorrect ? (isFraud ? 1 : 0) : (isFraud ? 0 : 1);

    if (isCorrect) {
      onFeedback(predictionId, actualClass, 'Prediction was correct');
    } else {
      setFeedbackType(actualClass);
      setShowFeedbackModal(true);
    }
  };

  const submitFeedbackWithNote = () => {
    if (!feedbackNote.trim()) {
      alert('Please provide feedback about what might be the issue');
      return;
    }

    onFeedback(predictionId, feedbackType, feedbackNote);
    setShowFeedbackModal(false);
    setFeedbackNote('');
  };

  return (
    <>
      <div className="mt-8 bg-gradient-to-br from-slate-900/90 to-slate-800/90 backdrop-blur-md rounded-3xl shadow-2xl overflow-hidden border border-cyan-500/20 animate-fadeIn">
        {/* Result Header */}
        <div className={`p-12 text-center relative overflow-hidden ${isFraud
          ? 'bg-gradient-to-r from-red-900/50 to-red-800/50 border-b-4 border-red-500'
          : 'bg-gradient-to-r from-green-900/50 to-green-800/50 border-b-4 border-green-500'
          }`}>
          {/* Animated Background Pattern */}
          <div className="absolute inset-0 opacity-10">
            <div className={`absolute inset-0 ${isFraud ? 'bg-red-500' : 'bg-green-500'} animate-pulse`}></div>
          </div>

          <div className="relative z-10">
            <div className="text-5xl mb-6 font-bold text-white animate-bounce">
              {isFraud ? 'Warning' : 'Safe'}
            </div>
            <h2 className="text-5xl font-black text-white mb-4 drop-shadow-lg">
              {isFraud ? 'FRAUD DETECTED!' : 'LEGITIMATE TRANSACTION'}
            </h2>
            <div className="flex justify-center items-center space-x-8 text-white text-xl mt-6">
              <div className="bg-black/30 px-6 py-3 rounded-xl backdrop-blur-sm">
                <span className="opacity-80">Confidence:</span>
                <span className="font-black ml-2 text-2xl">{confidence}%</span>
              </div>
              <div className="w-px h-8 bg-white opacity-50"></div>
              <div className="bg-black/30 px-6 py-3 rounded-xl backdrop-blur-sm">
                <span className="opacity-80">Risk Level:</span>
                <span className="font-black ml-2 text-2xl">{result.risk_level}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="h-2 bg-slate-900">
          <div
            className={`h-full transition-all duration-1000 ${isFraud ? 'bg-gradient-to-r from-red-500 to-red-600' : 'bg-gradient-to-r from-green-500 to-green-600'
              }`}
            style={{ width: `${confidence}%` }}
          ></div>
        </div>

        {/* AI Explanation */}
        <div className="p-8">
          <h3 className="text-3xl font-black text-cyan-300 mb-6 flex items-center">
            <span className="text-4xl mr-3">🤖</span>
            AI Analysis
          </h3>
          <div className="bg-slate-800/50 p-8 rounded-2xl border-l-4 border-cyan-500 backdrop-blur-sm">
            <p className="text-cyan-100 whitespace-pre-line leading-relaxed text-lg">
              {result.ai_explanation || 'AI analysis not available'}
            </p>
          </div>

          {/* Transaction Details */}
          <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className={`p-6 rounded-2xl border-2 ${predictionId ? 'bg-blue-900/20 border-blue-500/30' : 'bg-red-900/20 border-red-500/30'}`}>
              <p className="text-sm text-cyan-400 font-semibold mb-2">Prediction ID</p>
              <p className={`text-3xl font-black ${predictionId ? 'text-blue-400' : 'text-red-400'}`}>
                {predictionId ? `#${predictionId}` : '⚠️ Not Saved'}
              </p>
            </div>
            <div className="bg-purple-900/20 p-6 rounded-2xl border-2 border-purple-500/30">
              <p className="text-sm text-cyan-400 font-semibold mb-2">Model Type</p>
              <p className="text-3xl font-black text-purple-400">
                {result.mode === 'banking' ? '🏦 Banking' : '💳 Credit Card'}
              </p>
            </div>
          </div>
        </div>

        {/* Feedback Section */}
        {predictionId ? (
          <div className="p-8 pt-0">
            <div className="bg-slate-800/50 p-8 rounded-2xl border border-cyan-500/20">
              <h4 className="text-2xl font-bold text-cyan-300 mb-6 text-center">
                Was this prediction accurate?
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <button
                  onClick={() => handleFeedbackClick(true)}
                  className="bg-gradient-to-r from-green-600 to-green-700 text-white py-6 px-8 rounded-2xl font-bold text-xl hover:from-green-700 hover:to-green-800 transition-all hover:scale-105 shadow-lg shadow-green-500/30 border border-green-400/30"
                >
                  ✓ Yes, Correct
                </button>
                <button
                  onClick={() => handleFeedbackClick(false)}
                  className="bg-gradient-to-r from-red-600 to-red-700 text-white py-6 px-8 rounded-2xl font-bold text-xl hover:from-red-700 hover:to-red-800 transition-all hover:scale-105 shadow-lg shadow-red-500/30 border border-red-400/30"
                >
                  ✗ No, Incorrect
                </button>
              </div>
              <p className="text-sm text-cyan-400 mt-6 text-center">
                💡 Your feedback helps improve our AI model's accuracy
              </p>
            </div>
          </div>
        ) : (
          <div className="p-8 pt-0">
            <div className="bg-yellow-900/20 border-l-4 border-yellow-500 p-6 rounded-2xl backdrop-blur-sm">
              <p className="text-yellow-400 font-semibold text-lg">
                ⚠️ Feedback feature unavailable
              </p>
              <p className="text-yellow-300 text-sm mt-2">
                Database connection required to save predictions and collect feedback.
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Feedback Modal */}
      {showFeedbackModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 animate-fadeIn">
          <div className="bg-gradient-to-br from-slate-900 to-slate-800 border-2 border-cyan-500/30 rounded-3xl p-10 max-w-md w-full mx-4 shadow-2xl">
            <div className="text-center mb-8">
              <div className="text-6xl mb-4">📝</div>
              <h2 className="text-3xl font-black text-cyan-300 mb-3">
                Help Us Improve
              </h2>
              <p className="text-cyan-400">
                Please tell us what might be the issue with this prediction
              </p>
            </div>

            <textarea
              value={feedbackNote}
              onChange={(e) => setFeedbackNote(e.target.value)}
              className="w-full px-4 py-3 bg-slate-900/50 border-2 border-cyan-500/30 rounded-xl text-cyan-100 placeholder-cyan-700 focus:ring-2 focus:ring-cyan-500 focus:border-cyan-400 resize-none"
              rows="5"
              placeholder="Example: The transaction amount seems normal for this time of day, or the location is actually correct..."
            ></textarea>

            <div className="flex space-x-4 mt-8">
              <button
                onClick={() => {
                  setShowFeedbackModal(false);
                  setFeedbackNote('');
                }}
                className="flex-1 bg-slate-700 text-slate-300 py-4 px-6 rounded-xl font-semibold hover:bg-slate-600 transition"
              >
                Cancel
              </button>
              <button
                onClick={submitFeedbackWithNote}
                className="flex-1 bg-gradient-to-r from-cyan-500 to-blue-600 text-white py-4 px-6 rounded-xl font-semibold hover:from-cyan-600 hover:to-blue-700 transition shadow-lg shadow-cyan-500/30"
              >
                Submit Feedback
              </button>
            </div>
          </div>
        </div>
      )}

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
    </>
  );
}

export default ResultDisplay;