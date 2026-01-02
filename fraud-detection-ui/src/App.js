import React from 'react';
import { SignedIn, SignedOut, useUser } from '@clerk/clerk-react';
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import './App.css';

function App() {
  const { user, isLoaded } = useUser();

  // Show loading while Clerk loads
  if (!isLoaded) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-white"></div>
          <p className="text-white text-xl mt-4 font-semibold">Loading Fraud Detector...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      {/* When user is NOT signed in - Show Login/Signup */}
      <SignedOut>
        <Login />
      </SignedOut>
      
      {/* When user IS signed in - Show Dashboard */}
      <SignedIn>
        <Dashboard user={user} />
      </SignedIn>
    </div>
  );
}

export default App;