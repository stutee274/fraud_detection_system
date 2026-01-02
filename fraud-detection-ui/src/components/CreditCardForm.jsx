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

  return (
    <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow-lg">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Credit Card Transaction</h2>
        <div className="space-x-2">
          <button
            type="button"
            onClick={() => handleQuickFill('normal')}
            className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600"
          >
            Fill Normal
          </button>
          <button
            type="button"
            onClick={() => handleQuickFill('fraud')}
            className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600"
          >
            Fill Fraud
          </button>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Transaction Amount ($)
          </label>
          <input
            type="number"
            step="0.01"
            name="Amount"
            value={formData.Amount}
            onChange={handleChange}
            required
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary"
            placeholder="Enter amount"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Time (seconds)
          </label>
          <input
            type="number"
            name="Time"
            value={formData.Time}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary"
          />
        </div>
      </div>

      <div className="mb-4">
        <button
          type="button"
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="text-primary hover:text-blue-700 font-medium"
        >
          {showAdvanced ? '▼ Hide' : '▶ Show'} Advanced Features (V1-V28)
        </button>
      </div>

      {showAdvanced && (
        <div className="grid grid-cols-4 gap-3 mb-4 p-4 bg-gray-50 rounded-lg">
          {Array.from({ length: 28 }, (_, i) => i + 1).map((num) => (
            <div key={num}>
              <label className="block text-xs font-medium text-gray-600 mb-1">
                V{num}
              </label>
              <input
                type="number"
                step="0.01"
                name={`V${num}`}
                value={formData[`V${num}`]}
                onChange={handleChange}
                className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-1 focus:ring-primary"
              />
            </div>
          ))}
        </div>
      )}

      <p className="text-sm text-gray-600 mb-4">
        💡 Tip: Use quick-fill buttons to test with sample data
      </p>

      <button
        type="submit"
        disabled={loading}
        className={`w-full py-3 px-6 rounded-lg font-semibold text-white ${
          loading
            ? 'bg-gray-400 cursor-not-allowed'
            : 'bg-primary hover:bg-blue-700'
        }`}
      >
        {loading ? 'Analyzing...' : 'Check for Fraud'}
      </button>
    </form>
  );
}

export default CreditCardForm;