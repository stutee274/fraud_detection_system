import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import ModeSelector from '../components/ModeSelector';
import BankingForm from '../components/BankingForm';
import CreditCardForm from '../components/CreditCardForm';
import ResultDisplay from '../components/ResultDisplay';
import { checkFraud, submitFeedback, getStats } from '../services/api';  // ← Import getStats!

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
      const data = await getStats();  // ← Fixed!
      setStats(data);
    } catch (error) {
      console.error('Error loading stats:', error);
      alert('⚠️ Failed to load stats. Check console for details.');
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
      
      // Debug log
      console.log('Fraud check result:', data);
      
      setResult(data);

      setTimeout(() => {
        window.scrollTo({
          top: document.documentElement.scrollHeight,
          behavior: 'smooth'
        });
      }, 100);
      
    } catch (error) {
      console.error('Error:', error);
      alert('❌ Error checking fraud. Check console for details.');
    } finally {
      setLoading(false);
    }
  };

  const handleFeedback = async (predictionId, actualClass, note) => {
    try {
      console.log('Submitting feedback:', { predictionId, actualClass, note });
      
      await submitFeedback(predictionId, actualClass, note);
      alert('✅ Thank you for your feedback! This helps improve our AI model.');
      setResult(null);
      
      if (showStats) {
        loadStats();
      }
    } catch (error) {
      console.error('Error submitting feedback:', error);
      alert('❌ Error submitting feedback. Check console for details.');
    }
  };
}
 export default Dashboard;