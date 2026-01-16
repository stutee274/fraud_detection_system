import React, { useState } from 'react';

function CreditCardForm({ onSubmit, loading }) {
  const [formData, setFormData] = useState({
    Time: '0',
    Amount: '',
    V1: '0', V2: '0', V3: '0', V4: '0', V5: '0',
    V6: '0', V7: '0', V8: '0', V9: '0', V10: '0',
    V11: '0', V12: '0', V13: '0', V14: '0', V15: '0',
    V16: '0', V17: '0', V18: '0', V19: '0', V20: '0',
    V21: '0', V22: '0', V23: '0', V24: '0', V25: '0',
    V26: '0', V27: '0', V28: '0'
  });

  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const handleQuickFill = (type) => {
    if (type === 'normal') {
      setFormData({
        Time: '35000',
        Amount: '89',
        V1: '0.45', V2: '0.62', V3: '-0.22', V4: '0.72', V5: '0.28',
        V6: '0.52', V7: '-0.28', V8: '0.42', V9: '0.22', V10: '0.55',
        V11: '0.38', V12: '0.22', V13: '-0.22', V14: '0.48', V15: '0.28',
        V16: '0.45', V17: '-0.28', V18: '0.28', V19: '0.22', V20: '0.28',
        V21: '0.45', V22: '0.28', V23: '0.22', V24: '0.28', V25: '0.22',
        V26: '0.28', V27: '0.22', V28: '0.22'
      });
    } else {
      setFormData({
        Time: '68000',
        Amount: '225',
        V1: '-0.75', V2: '0.85', V3: '0.12', V4: '0.58', V5: '-0.12',
        V6: '0.32', V7: '0.12', V8: '0.05', V9: '-0.18', V10: '0.95',
        V11: '0.68', V12: '-1.15', V13: '0.32', V14: '-2.15', V15: '0.48',
        V16: '-0.58', V17: '-1.28', V18: '-0.42', V19: '0.18', V20: '0.08',
        V21: '0.25', V22: '0.38', V23: '-0.08', V24: '-0.28', V25: '0.25',
        V26: '-0.38', V27: '0.02', V28: '0.02'
      });
    }
  };

  const inputClasses = "w-full px-4 py-3 bg-slate-900/50 border border-purple-500/30 rounded-xl text-purple-100 placeholder-purple-700 focus:ring-2 focus:ring-purple-500 focus:border-purple-400 transition-all duration-200 backdrop-blur-sm";
  const labelClasses = "block text-sm font-semibold text-purple-300 mb-2";
  const smallInputClasses = "w-full px-2 py-1.5 text-sm bg-slate-900/50 border border-purple-500/30 rounded-lg text-purple-100 focus:ring-1 focus:ring-purple-500 focus:border-purple-400 transition-all duration-200";

  return (
    <form onSubmit={handleSubmit} className="bg-gradient-to-br from-slate-900/80 to-slate-800/80 backdrop-blur-md p-8 rounded-3xl shadow-2xl border border-purple-500/20">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8 gap-4">
        <h2 className="text-3xl font-black text-purple-300 flex items-center">
          <span className="text-purple-400 mr-3">💳</span>
          Credit Card Transaction
        </h2>
        <div className="flex flex-wrap gap-3">
          <button
            type="button"
            onClick={() => handleQuickFill('normal')}
            className="px-5 py-2.5 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-xl hover:from-green-700 hover:to-emerald-700 font-bold shadow-lg shadow-green-500/30 hover:shadow-green-500/50 transition-all duration-200 border border-green-400/30"
          >
            ✓ Fill Normal
          </button>
          <button
            type="button"
            onClick={() => handleQuickFill('fraud')}
            className="px-5 py-2.5 bg-gradient-to-r from-red-600 to-pink-600 text-white rounded-xl hover:from-red-700 hover:to-pink-700 font-bold shadow-lg shadow-red-500/30 hover:shadow-red-500/50 transition-all duration-200 border border-red-400/30"
          >
            ⚠ Fill Fraud
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div>
          <label className={labelClasses}>
            Transaction Amount ($)
          </label>
          <input
            type="number"
            step="0.01"
            name="Amount"
            value={formData.Amount}
            onChange={handleChange}
            required
            className={inputClasses}
            placeholder="Enter amount"
          />
        </div>

        <div>
          <label className={labelClasses}>
            Time (seconds)
          </label>
          <input
            type="number"
            name="Time"
            value={formData.Time}
            onChange={handleChange}
            className={inputClasses}
            placeholder="Time since first transaction"
          />
        </div>
      </div>

      <div className="mb-6">
        <button
          type="button"
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="flex items-center space-x-2 text-purple-400 hover:text-purple-300 font-bold transition-colors group"
        >
          <span className={`transform transition-transform duration-200 ${showAdvanced ? 'rotate-90' : ''}`}>
            ▶
          </span>
          <span>{showAdvanced ? 'Hide' : 'Show'} Advanced Features (V1-V28)</span>
          <div className="h-px flex-1 bg-gradient-to-r from-purple-500/50 to-transparent ml-3"></div>
        </button>
      </div>

      {showAdvanced && (
        <div className="mb-6 p-6 bg-slate-800/50 rounded-2xl border border-purple-500/20 animate-slideDown">
          <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-7 gap-3">
            {Array.from({ length: 28 }, (_, i) => i + 1).map((num) => (
              <div key={num}>
                <label className="block text-xs font-bold text-purple-400 mb-1">
                  V{num}
                </label>
                <input
                  type="number"
                  step="0.01"
                  name={`V${num}`}
                  value={formData[`V${num}`]}
                  onChange={handleChange}
                  className={smallInputClasses}
                />
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="mb-6 p-4 bg-purple-900/20 border-l-4 border-purple-500 rounded-xl backdrop-blur-sm">
        <p className="text-sm text-purple-300 flex items-center">
          <span className="text-2xl mr-2">💡</span>
          <span><strong>Tip:</strong> Use quick-fill buttons to test with sample data or manually enter V1-V28 PCA features</span>
        </p>
      </div>

      <button
        type="submit"
        disabled={loading}
        className={`w-full mt-2 py-4 px-6 rounded-2xl font-bold text-lg transition-all duration-300 transform hover:scale-105 ${loading
            ? 'bg-slate-700 cursor-not-allowed text-slate-400'
            : 'bg-gradient-to-r from-purple-500 to-pink-600 hover:from-purple-600 hover:to-pink-700 text-white shadow-lg shadow-purple-500/50 hover:shadow-purple-500/70'
          }`}
      >
        {loading ? (
          <span className="flex items-center justify-center">
            <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Analyzing Transaction...
          </span>
        ) : (
          '🔍 Check for Fraud'
        )}
      </button>

      <style jsx>{`
        @keyframes slideDown {
          from {
            opacity: 0;
            transform: translateY(-10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .animate-slideDown {
          animation: slideDown 0.3s ease-out;
        }
      `}</style>
    </form>
  );
}

export default CreditCardForm;