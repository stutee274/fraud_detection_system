import React, { useState, useEffect } from 'react';
import { getStats } from '../services/api';

function StatsDashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const data = await getStats();
      setStats(data);
    } catch (error) {
      console.error('Error loading stats:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white p-8 rounded-lg shadow-lg text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
        <p className="mt-4 text-gray-600">Loading statistics...</p>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="bg-white p-8 rounded-lg shadow-lg text-center">
        <p className="text-red-600">Failed to load statistics</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">System Statistics</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Total Predictions */}
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white p-6 rounded-lg shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100 text-sm">Total Predictions</p>
              <p className="text-4xl font-bold mt-2">
                {stats.total_predictions || 0}
              </p>
            </div>
            <div className="text-5xl opacity-50">📊</div>
          </div>
        </div>

        {/* With Feedback */}
        <div className="bg-gradient-to-br from-green-500 to-green-600 text-white p-6 rounded-lg shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100 text-sm">With Feedback</p>
              <p className="text-4xl font-bold mt-2">
                {stats.with_feedback || 0}
              </p>
            </div>
            <div className="text-5xl opacity-50">✅</div>
          </div>
        </div>

        {/* Feedback Rate */}
        <div className="bg-gradient-to-br from-purple-500 to-purple-600 text-white p-6 rounded-lg shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-100 text-sm">Feedback Rate</p>
              <p className="text-4xl font-bold mt-2">
                {stats.feedback_rate || 0}%
              </p>
            </div>
            <div className="text-5xl opacity-50">📈</div>
          </div>
        </div>
      </div>

      {/* Model Breakdown */}
      {stats.by_model && (
        <div className="bg-white p-6 rounded-lg shadow-lg">
          <h3 className="text-xl font-semibold mb-4">By Model Type</h3>
          <div className="grid grid-cols-2 gap-4">
            <div className="border-l-4 border-blue-500 pl-4">
              <p className="text-gray-600 text-sm">Banking Feedback</p>
              <p className="text-2xl font-bold text-blue-600">
                {stats.by_model.banking || 0}
              </p>
            </div>
            <div className="border-l-4 border-purple-500 pl-4">
              <p className="text-gray-600 text-sm">Credit Card Feedback</p>
              <p className="text-2xl font-bold text-purple-600">
                {stats.by_model.credit_card || 0}
              </p>
            </div>
          </div>
        </div>
      )}

      <button
        onClick={loadStats}
        className="w-full bg-primary text-white py-3 rounded-lg font-semibold hover:bg-blue-700"
      >
        🔄 Refresh Statistics
      </button>
    </div>
  );
}

export default StatsDashboard;