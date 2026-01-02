import React, { useState } from 'react';

function ResultDisplay({ result, onFeedback }) {
  const [showFeedbackModal, setShowFeedbackModal] = useState(false);
  const [feedbackType, setFeedbackType] = useState(null);
  const [feedbackNote, setFeedbackNote] = useState('');

  if (!result) return null;

  const isFraud = result.is_fraud;
  const confidence = (result.fraud_probability * 100).toFixed(2);

  const handleFeedbackClick = (isCorrect) => {
    const actualClass = isCorrect ? (isFraud ? 1 : 0) : (isFraud ? 0 : 1);
    
    if (isCorrect) {
      // If correct, submit immediately
      onFeedback(result.prediction_id, actualClass, 'Prediction was correct');
    } else {
      // If wrong, show modal to get feedback note
      setFeedbackType(actualClass);
      setShowFeedbackModal(true);
    }
  };

  const submitFeedbackWithNote = () => {
    if (!feedbackNote.trim()) {
      alert('Please provide feedback about what might be the issue');
      return;
    }
    
    onFeedback(result.prediction_id, feedbackType, feedbackNote);
    setShowFeedbackModal(false);
    setFeedbackNote('');
  };

  return (
    <>
      <div className="mt-8 bg-white rounded-xl shadow-xl overflow-hidden">
        {/* Result Header */}
        <div className={`p-8 text-center ${
          isFraud 
            ? 'bg-gradient-to-r from-red-500 to-red-600' 
            : 'bg-gradient-to-r from-green-500 to-green-600'
        }`}>
          <div className="text-8xl mb-4 animate-bounce">
            {isFraud ? '⚠️' : '✅'}
          </div>
          <h2 className="text-4xl font-bold text-white mb-2">
            {isFraud ? 'FRAUD DETECTED!' : 'LEGITIMATE TRANSACTION'}
          </h2>
          <div className="flex justify-center items-center space-x-6 text-white text-lg mt-4">
            <div>
              <span className="opacity-80">Confidence:</span>
              <span className="font-bold ml-2">{confidence}%</span>
            </div>
            <div className="w-px h-6 bg-white opacity-50"></div>
            <div>
              <span className="opacity-80">Risk Level:</span>
              <span className="font-bold ml-2">{result.risk_level}</span>
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="h-3 bg-gray-200">
          <div 
            className={`h-full transition-all duration-1000 ${
              isFraud ? 'bg-red-600' : 'bg-green-600'
            }`}
            style={{ width: `${confidence}%` }}
          ></div>
        </div>

        {/* AI Explanation */}
        <div className="p-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
            <span className="text-3xl mr-3">🤖</span>
            AI Analysis
          </h3>
          <div className="bg-gray-50 p-6 rounded-lg border-l-4 border-primary">
            <p className="text-gray-800 whitespace-pre-line leading-relaxed">
              {result.explanation}
            </p>
          </div>

          {/* Transaction Details */}
          <div className="mt-6 grid grid-cols-2 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <p className="text-sm text-gray-600">Prediction ID</p>
              <p className="text-xl font-bold text-primary">
                #{result.prediction_id}
              </p>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg">
              <p className="text-sm text-gray-600">Model Type</p>
              <p className="text-xl font-bold text-purple-600">
                {result.mode === 'banking' ? '🏦 Banking' : '💳 Credit Card'}
              </p>
            </div>
          </div>
        </div>

        {/* Feedback Section */}
        <div className="p-8 pt-0">
          <div className="bg-gray-100 p-6 rounded-lg">
            <h4 className="text-lg font-semibold text-gray-900 mb-4 text-center">
              Was this prediction accurate?
            </h4>
            <div className="grid grid-cols-2 gap-4">
              <button
                onClick={() => handleFeedbackClick(true)}
                className="bg-green-500 text-white py-4 px-6 rounded-lg font-bold text-lg hover:bg-green-600 transition-all hover:scale-105 shadow-lg"
              >
                ✓ Yes, Correct
              </button>
              <button
                onClick={() => handleFeedbackClick(false)}
                className="bg-red-500 text-white py-4 px-6 rounded-lg font-bold text-lg hover:bg-red-600 transition-all hover:scale-105 shadow-lg"
              >
                ✗ No, Incorrect
              </button>
            </div>
            <p className="text-sm text-gray-600 mt-4 text-center">
              💡 Your feedback helps improve our AI model's accuracy
            </p>
          </div>
        </div>
      </div>

      {/* Feedback Modal */}
      {showFeedbackModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4 shadow-2xl">
            <div className="text-center mb-6">
              <div className="text-5xl mb-4">📝</div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Help Us Improve
              </h2>
              <p className="text-gray-600">
                Please tell us what might be the issue with this prediction
              </p>
            </div>
            
            <textarea
              value={feedbackNote}
              onChange={(e) => setFeedbackNote(e.target.value)}
              className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent resize-none"
              rows="5"
              placeholder="Example: The transaction amount seems normal for this time of day, or the location is actually correct..."
            ></textarea>

            <div className="flex space-x-4 mt-6">
              <button
                onClick={() => {
                  setShowFeedbackModal(false);
                  setFeedbackNote('');
                }}
                className="flex-1 bg-gray-200 text-gray-700 py-3 px-6 rounded-lg font-semibold hover:bg-gray-300 transition"
              >
                Cancel
              </button>
              <button
                onClick={submitFeedbackWithNote}
                className="flex-1 bg-primary text-white py-3 px-6 rounded-lg font-semibold hover:bg-blue-700 transition"
              >
                Submit Feedback
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default ResultDisplay;