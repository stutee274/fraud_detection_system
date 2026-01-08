import React, { useState } from 'react';

function ResultDisplay({ result, onFeedback }) {
  const [showFeedbackModal, setShowFeedbackModal] = useState(false);
  const [feedbackType, setFeedbackType] = useState(null);
  const [feedbackNote, setFeedbackNote] = useState('');

  if (!result) return null;

  // Debug: Check if prediction_id exists
  console.log('Result data:', result);
  
  const isFraud = result.is_fraud;
  const confidence = (result.fraud_probability * 100).toFixed(2);
  const predictionId = result.prediction_id;

  // Check if prediction_id exists
  if (!predictionId) {
    console.error('⚠️ Missing prediction_id in result!', result);
  }

  const handleFeedbackClick = (isCorrect) => {
    // Safety check
    if (!predictionId) {
      alert('⚠️ Cannot submit feedback: Prediction ID is missing. This transaction was not saved to database.');
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
    
    if (!predictionId) {
      alert('⚠️ Cannot submit feedback: Prediction ID is missing.');
      return;
    }
    
    onFeedback(predictionId, feedbackType, feedbackNote);
    setShowFeedbackModal(false);
    setFeedbackNote('');
  };

  return (
    <>
      <div className="mt-8 bg-white rounded-xl shadow-xl overflow-hidden">
        {/* ... your existing JSX stays the same ... */}
        
        {/* Update the Prediction ID display to show warning if missing */}
        <div className="mt-6 grid grid-cols-2 gap-4">
          <div className={`p-4 rounded-lg ${predictionId ? 'bg-blue-50' : 'bg-red-50'}`}>
            <p className="text-sm text-gray-600">Prediction ID</p>
            <p className={`text-xl font-bold ${predictionId ? 'text-primary' : 'text-red-600'}`}>
              {predictionId ? `#${predictionId}` : '⚠️ Not Saved'}
            </p>
          </div>
          {/* ... rest of your display stays same ... */}
        </div>
        
        {/* ... rest of your component ... */}
      </div>
      
      {/* ... modal stays the same ... */}
    </>
  );
}

export default ResultDisplay;