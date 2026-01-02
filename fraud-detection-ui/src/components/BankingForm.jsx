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

  return (
    <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold mb-6">Banking Transaction Details</h2>
      
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Transaction Amount ($)
          </label>
          <input
            type="number"
            name="Transaction_Amount"
            value={formData.Transaction_Amount}
            onChange={handleChange}
            required
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary"
            placeholder="Enter amount"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Account Balance ($)
          </label>
          <input
            type="number"
            name="Account_Balance"
            value={formData.Account_Balance}
            onChange={handleChange}
            required
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary"
            placeholder="Enter balance"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Transaction Type
          </label>
          <select
            name="Transaction_Type"
            value={formData.Transaction_Type}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary"
          >
            <option value="POS">POS</option>
            <option value="Online">Online</option>
            <option value="ATM Withdrawal">ATM Withdrawal</option>
            <option value="Transfer">Transfer</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Transaction Date & Time
          </label>
          <input
            type="datetime-local"
            name="Timestamp"
            value={formData.Timestamp}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Daily Transaction Count
          </label>
          <input
            type="number"
            name="Daily_Transaction_Count"
            value={formData.Daily_Transaction_Count}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            7-Day Average Amount ($)
          </label>
          <input
            type="number"
            name="Avg_Transaction_Amount_7d"
            value={formData.Avg_Transaction_Amount_7d}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary"
            placeholder="Average amount"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Failed Transactions (7 days)
          </label>
          <input
            type="number"
            name="Failed_Transaction_Count_7d"
            value={formData.Failed_Transaction_Count_7d}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Card Age (days)
          </label>
          <input
            type="number"
            name="Card_Age"
            value={formData.Card_Age}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Transaction Distance (km)
          </label>
          <input
            type="number"
            name="Transaction_Distance"
            value={formData.Transaction_Distance}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Suspicious IP?
          </label>
          <select
            name="IP_Address_Flag"
            value={formData.IP_Address_Flag}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary"
          >
            <option value="0">No</option>
            <option value="1">Yes</option>
          </select>
        </div>
      </div>

      <button
        type="submit"
        disabled={loading}
        className={`w-full mt-6 py-3 px-6 rounded-lg font-semibold text-white ${
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

export default BankingForm;