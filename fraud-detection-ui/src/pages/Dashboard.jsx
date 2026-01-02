// import React, { useState, useEffect } from 'react';
// import Navbar from '../components/Navbar';
// import ModeSelector from '../components/ModeSelector';
// import BankingForm from '../components/BankingForm';
// import CreditCardForm from '../components/CreditCardForm';
// import ResultDisplay from '../components/ResultDisplay';
// import { checkFraud, submitFeedback } from '../services/api';
// import axios from 'axios';

// function Dashboard({ user, onLogout }) {
//   const [mode, setMode] = useState('banking');
//   const [result, setResult] = useState(null);
//   const [loading, setLoading] = useState(false);
//   const [showStats, setShowStats] = useState(false);
//   const [stats, setStats] = useState(null);
//   const [totalUsers, setTotalUsers] = useState(0);

//   useEffect(() => {
//     // Get total users from localStorage
//     const users = JSON.parse(localStorage.getItem('registeredUsers') || '[]');
//     setTotalUsers(users.length);
//   }, []);

//   const loadStats = async () => {
//     try {
//       const response = await axios.get('http://localhost:5000/api/stats');
//       setStats(response.data);
//     } catch (error) {
//       console.error('Error loading stats:', error);
//     }
//   };

//   const handleShowStats = () => {
//     setShowStats(!showStats);
//     if (!showStats) {
//       loadStats();
//     }
//   };

//   const handleCheckFraud = async (formData) => {
//     setLoading(true);
//     setResult(null);
    
//     try {
//       if (mode === 'banking') {
//         const timestamp = formData.Timestamp.replace('T', ' ') + ':00';
//         formData = { ...formData, Timestamp: timestamp };
//       }
      
//       const data = await checkFraud(mode, formData);
//       setResult(data);

//       // Scroll to result
//       setTimeout(() => {
//         window.scrollTo({
//           top: document.documentElement.scrollHeight,
//           behavior: 'smooth'
//         });
//       }, 100);
      
//     } catch (error) {
//       console.error('Error:', error);
//       alert('❌ Error checking fraud. Make sure Flask is running on port 5000!');
//     } finally {
//       setLoading(false);
//     }
//   };

//   const handleFeedback = async (predictionId, actualClass, note) => {
//     try {
//       await submitFeedback(predictionId, actualClass, note);
//       alert('✅ Thank you for your feedback! This helps improve our AI model.');
//       setResult(null);
      
//       // Reload stats if showing
//       if (showStats) {
//         loadStats();
//       }
//     } catch (error) {
//       console.error('Error:', error);
//       alert('❌ Error submitting feedback');
//     }
//   };

//   return (
//     <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
//       <Navbar user={user} onLogout={onLogout} />
      
//       <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
//         {/* Page Header */}
//         <div className="flex justify-between items-center mb-12">
//           <div>
//             <h1 className="text-5xl font-extrabold text-gray-900 mb-2">
//               Fraud Detection Dashboard
//             </h1>
//             <p className="text-xl text-gray-600">
//               AI-powered fraud detection for banking and credit card transactions
//             </p>
//           </div>
//           <button
//             onClick={handleShowStats}
//             className="bg-primary text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition shadow-lg"
//           >
//             {showStats ? '📊 Hide Stats' : '📊 Show Stats'}
//           </button>
//         </div>

//         {/* Stats Dashboard */}
//         {showStats && stats && (
//           <div className="mb-8">
//             <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
//               {/* Total Predictions */}
//               <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white p-6 rounded-lg shadow-lg">
//                 <div className="flex items-center justify-between">
//                   <div>
//                     <p className="text-blue-100 text-sm">Total Predictions</p>
//                     <p className="text-4xl font-bold mt-2">
//                       {stats.total_predictions || 0}
//                     </p>
//                   </div>
//                   <div className="text-5xl opacity-50">📊</div>
//                 </div>
//               </div>

//               {/* With Feedback */}
//               <div className="bg-gradient-to-br from-green-500 to-green-600 text-white p-6 rounded-lg shadow-lg">
//                 <div className="flex items-center justify-between">
//                   <div>
//                     <p className="text-green-100 text-sm">With Feedback</p>
//                     <p className="text-4xl font-bold mt-2">
//                       {stats.with_feedback || 0}
//                     </p>
//                   </div>
//                   <div className="text-5xl opacity-50">✅</div>
//                 </div>
//               </div>

//               {/* Feedback Rate */}
//               <div className="bg-gradient-to-br from-purple-500 to-purple-600 text-white p-6 rounded-lg shadow-lg">
//                 <div className="flex items-center justify-between">
//                   <div>
//                     <p className="text-purple-100 text-sm">Feedback Rate</p>
//                     <p className="text-4xl font-bold mt-2">
//                       {stats.feedback_rate || 0}%
//                     </p>
//                   </div>
//                   <div className="text-5xl opacity-50">📈</div>
//                 </div>
//               </div>

//               {/* Registered Users */}
//               <div className="bg-gradient-to-br from-orange-500 to-orange-600 text-white p-6 rounded-lg shadow-lg">
//                 <div className="flex items-center justify-between">
//                   <div>
//                     <p className="text-orange-100 text-sm">Registered Users</p>
//                     <p className="text-4xl font-bold mt-2">
//                       {totalUsers}
//                     </p>
//                   </div>
//                   <div className="text-5xl opacity-50">👥</div>
//                 </div>
//               </div>
//             </div>
//           </div>
//         )}
        
//         {/* Mode Selector */}
//         <ModeSelector mode={mode} setMode={setMode} />
        
//         {/* Forms */}
//         {mode === 'banking' ? (
//           <BankingForm onSubmit={handleCheckFraud} loading={loading} />
//         ) : (
//           <CreditCardForm onSubmit={handleCheckFraud} loading={loading} />
//         )}
        
//         {/* Result Display */}
//         <ResultDisplay result={result} onFeedback={handleFeedback} />
//       </div>
//     </div>
//   );
// }

// export default Dashboard;


import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import ModeSelector from '../components/ModeSelector';
import BankingForm from '../components/BankingForm';
import CreditCardForm from '../components/CreditCardForm';
import ResultDisplay from '../components/ResultDisplay';
import { checkFraud, submitFeedback } from '../services/api';
import axios from 'axios';

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
      const response = await axios.get('http://localhost:5000/api/stats');
      setStats(response.data);
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
      setResult(data);

      setTimeout(() => {
        window.scrollTo({
          top: document.documentElement.scrollHeight,
          behavior: 'smooth'
        });
      }, 100);
      
    } catch (error) {
      console.error('Error:', error);
      alert('❌ Error checking fraud. Make sure Flask is running on port 5000!');
    } finally {
      setLoading(false);
    }
  };

  const handleFeedback = async (predictionId, actualClass, note) => {
    try {
      await submitFeedback(predictionId, actualClass, note);
      alert('✅ Thank you for your feedback! This helps improve our AI model.');
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
        {/* Enhanced Page Header */}
        <div className="mb-12">
          <div className="flex justify-between items-center flex-wrap gap-4">
            <div>
              <h1 className="text-5xl font-extrabold bg-gradient-to-r from-purple-600 via-pink-600 to-red-600 bg-clip-text text-transparent mb-3">
                Fraud Detection Dashboard
              </h1>
              <p className="text-xl text-gray-600 font-medium flex items-center space-x-2">
                <span>🤖</span>
                <span>AI-powered fraud detection for banking and credit card transactions</span>
              </p>
            </div>
            <button
              onClick={handleShowStats}
              className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-8 py-4 rounded-2xl font-bold hover:from-purple-700 hover:to-pink-700 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105 flex items-center space-x-2"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              <span>{showStats ? 'Hide Stats' : 'Show Stats'}</span>
            </button>
          </div>
        </div>

        {/* Enhanced Stats Dashboard */}
        {showStats && stats && (
          <div className="mb-8 animate-fadeIn">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {/* Total Predictions */}
              <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white p-8 rounded-3xl shadow-xl transform hover:scale-105 transition-all duration-200">
                <div className="flex items-center justify-between mb-4">
                  <div className="bg-white/20 p-4 rounded-2xl backdrop-blur-sm">
                    <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>
                  <div className="text-6xl font-black opacity-20">📊</div>
                </div>
                <p className="text-blue-100 text-sm font-semibold mb-2">Total Predictions</p>
                <p className="text-5xl font-black mb-2">
                  {stats.total_predictions?.toLocaleString() || 0}
                </p>
                <p className="text-blue-100 text-xs">All-time transactions analyzed</p>
              </div>

              {/* With Feedback */}
              <div className="bg-gradient-to-br from-green-500 to-green-600 text-white p-8 rounded-3xl shadow-xl transform hover:scale-105 transition-all duration-200">
                <div className="flex items-center justify-between mb-4">
                  <div className="bg-white/20 p-4 rounded-2xl backdrop-blur-sm">
                    <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div className="text-6xl font-black opacity-20">✅</div>
                </div>
                <p className="text-green-100 text-sm font-semibold mb-2">With Feedback</p>
                <p className="text-5xl font-black mb-2">
                  {stats.with_feedback?.toLocaleString() || 0}
                </p>
                <p className="text-green-100 text-xs">User-verified predictions</p>
              </div>

              {/* Feedback Rate */}
              <div className="bg-gradient-to-br from-purple-500 to-purple-600 text-white p-8 rounded-3xl shadow-xl transform hover:scale-105 transition-all duration-200">
                <div className="flex items-center justify-between mb-4">
                  <div className="bg-white/20 p-4 rounded-2xl backdrop-blur-sm">
                    <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                    </svg>
                  </div>
                  <div className="text-6xl font-black opacity-20">📈</div>
                </div>
                <p className="text-purple-100 text-sm font-semibold mb-2">Feedback Rate</p>
                <p className="text-5xl font-black mb-2">
                  {stats.feedback_rate || 0}%
                </p>
                <p className="text-purple-100 text-xs">User engagement score</p>
              </div>

              {/* Registered Users */}
              <div className="bg-gradient-to-br from-orange-500 to-orange-600 text-white p-8 rounded-3xl shadow-xl transform hover:scale-105 transition-all duration-200">
                <div className="flex items-center justify-between mb-4">
                  <div className="bg-white/20 p-4 rounded-2xl backdrop-blur-sm">
                    <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                    </svg>
                  </div>
                  <div className="text-6xl font-black opacity-20">👥</div>
                </div>
                <p className="text-orange-100 text-sm font-semibold mb-2">Active Users</p>
                <p className="text-5xl font-black mb-2">
                  {totalUsers.toLocaleString()}
                </p>
                <p className="text-orange-100 text-xs">Registered accounts</p>
              </div>
            </div>
          </div>
        )}
        
        {/* Mode Selector */}
        <ModeSelector mode={mode} setMode={setMode} />
        
        {/* Forms */}
        {mode === 'banking' ? (
          <BankingForm onSubmit={handleCheckFraud} loading={loading} />
        ) : (
          <CreditCardForm onSubmit={handleCheckFraud} loading={loading} />
        )}
        
        {/* Result Display */}
        <ResultDisplay result={result} onFeedback={handleFeedback} />
      </div>

      <style jsx>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        
        .animate-fadeIn {
          animation: fadeIn 0.5s ease-out;
        }
      `}</style>
    </div>
  );
}

export default Dashboard;
