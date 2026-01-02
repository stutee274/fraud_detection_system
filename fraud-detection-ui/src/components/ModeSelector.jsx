import React from 'react';

function ModeSelector({ mode, setMode }) {
  return (
    <div className="flex space-x-4 mb-8">
      <button
        onClick={() => setMode('banking')}
        className={`flex-1 py-6 px-4 rounded-lg font-semibold text-lg transition-all ${
          mode === 'banking'
            ? 'bg-primary text-white shadow-lg scale-105'
            : 'bg-white text-gray-700 hover:bg-gray-50'
        }`}
      >
        <div className="text-4xl mb-2">🏦</div>
        Banking Fraud
      </button>
      
      <button
        onClick={() => setMode('credit_card')}
        className={`flex-1 py-6 px-4 rounded-lg font-semibold text-lg transition-all ${
          mode === 'credit_card'
            ? 'bg-primary text-white shadow-lg scale-105'
            : 'bg-white text-gray-700 hover:bg-gray-50'
        }`}
      >
        <div className="text-4xl mb-2">💳</div>
        Credit Card Fraud
      </button>
    </div>
  );
}

export default ModeSelector;