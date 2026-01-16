import React, { useState } from 'react';

function BankingForm({ onSubmit, loading }) {
  const [formData, setFormData] = useState({
    Transaction_Amount: '',
    Account_Balance: '',
    Transaction_Type: 'POS',
    Timestamp: new Date().toISOString().slice(0, 16),
    Daily_Transaction_Count: '1',
    Avg_Transaction_Amount_7d: '',
    Failed_Transaction_Count_7d: '0',
    Card_Age: '100',
    Transaction_Distance: '500',
    IP_Address_Flag: '0'
  });

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

  const inputClasses = "w-full px-4 py-3 bg-slate-900/50 border border-cyan-500/30 rounded-xl text-cyan-100 placeholder-cyan-700 focus:ring-2 focus:ring-cyan-500 focus:border-cyan-400 transition-all duration-200 backdrop-blur-sm";
  const labelClasses = "block text-sm font-semibold text-cyan-300 mb-2";

  return (
    <form onSubmit={handleSubmit} className="bg-gradient-to-br from-slate-900/80 to-slate-800/80 backdrop-blur-md p-8 rounded-3xl shadow-2xl border border-cyan-500/20">
      <h2 className="text-3xl font-black text-cyan-300 mb-8 flex items-center">
        <span className="text-cyan-400 mr-3">⚡</span>
        Banking Transaction Details
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className={labelClasses}>
            Transaction Amount ($)
          </label>
          <input
            type="number"
            step="0.01"
            name="Transaction_Amount"
            value={formData.Transaction_Amount}
            onChange={handleChange}
            required
            className={inputClasses}
            placeholder="Enter amount"
          />
        </div>

        <div>
          <label className={labelClasses}>
            Account Balance ($)
          </label>
          <input
            type="number"
            step="0.01"
            name="Account_Balance"
            value={formData.Account_Balance}
            onChange={handleChange}
            required
            className={inputClasses}
            placeholder="Enter balance"
          />
        </div>

        <div>
          <label className={labelClasses}>
            Transaction Type
          </label>
          <select
            name="Transaction_Type"
            value={formData.Transaction_Type}
            onChange={handleChange}
            className={inputClasses}
          >
            <option value="POS" className="bg-slate-900">POS</option>
            <option value="Online" className="bg-slate-900">Online</option>
            <option value="ATM Withdrawal" className="bg-slate-900">ATM Withdrawal</option>
            <option value="Transfer" className="bg-slate-900">Transfer</option>
          </select>
        </div>

        <div>
          <label className={labelClasses}>
            Transaction Date & Time
          </label>
          <input
            type="datetime-local"
            name="Timestamp"
            value={formData.Timestamp}
            onChange={handleChange}
            className={inputClasses}
          />
        </div>

        <div>
          <label className={labelClasses}>
            Daily Transaction Count
          </label>
          <input
            type="number"
            name="Daily_Transaction_Count"
            value={formData.Daily_Transaction_Count}
            onChange={handleChange}
            className={inputClasses}
          />
        </div>

        <div>
          <label className={labelClasses}>
            7-Day Average Amount ($)
          </label>
          <input
            type="number"
            step="0.01"
            name="Avg_Transaction_Amount_7d"
            value={formData.Avg_Transaction_Amount_7d}
            onChange={handleChange}
            className={inputClasses}
            placeholder="Average amount"
          />
        </div>

        <div>
          <label className={labelClasses}>
            Failed Transactions (7 days)
          </label>
          <input
            type="number"
            name="Failed_Transaction_Count_7d"
            value={formData.Failed_Transaction_Count_7d}
            onChange={handleChange}
            className={inputClasses}
          />
        </div>

        <div>
          <label className={labelClasses}>
            Card Age (days)
          </label>
          <input
            type="number"
            name="Card_Age"
            value={formData.Card_Age}
            onChange={handleChange}
            className={inputClasses}
          />
        </div>

        <div>
          <label className={labelClasses}>
            Transaction Distance (km)
          </label>
          <input
            type="number"
            step="0.01"
            name="Transaction_Distance"
            value={formData.Transaction_Distance}
            onChange={handleChange}
            className={inputClasses}
          />
        </div>

        <div>
          <label className={labelClasses}>
            Suspicious IP?
          </label>
          <select
            name="IP_Address_Flag"
            value={formData.IP_Address_Flag}
            onChange={handleChange}
            className={inputClasses}
          >
            <option value="0" className="bg-slate-900">No</option>
            <option value="1" className="bg-slate-900">Yes</option>
          </select>
        </div>
      </div>

      <button
        type="submit"
        disabled={loading}
        className={`w-full mt-8 py-4 px-6 rounded-2xl font-bold text-lg transition-all duration-300 transform hover:scale-105 ${loading
            ? 'bg-slate-700 cursor-not-allowed text-slate-400'
            : 'bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white shadow-lg shadow-cyan-500/50 hover:shadow-cyan-500/70'
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
    </form>
  );
}

export default BankingForm;