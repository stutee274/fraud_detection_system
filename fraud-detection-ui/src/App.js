import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { SignedIn, SignedOut, useUser } from '@clerk/clerk-react';
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';

const DashboardWrapper = () => {
  const { user } = useUser();
  return <Dashboard user={user} />;
};

function App() {
  const clerkPubKey = process.env.REACT_APP_CLERK_PUBLISHABLE_KEY;

  if (!clerkPubKey) {
    // Demo mode - no auth
    return (
      <Router>
        <Routes>
          <Route 
            path="/" 
            element={
              <Dashboard 
                user={{ 
                  fullName: 'Demo User', 
                  primaryEmailAddress: { emailAddress: 'demo@example.com' },
                  imageUrl: 'https://via.placeholder.com/150'
                }} 
              />
            } 
          />
          {/* Redirect all other routes to dashboard in demo mode */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    );
  }

  return (
    <Router>
      <Routes>
        <Route
          path="/"
          element={
            <>
              <SignedIn>
                <DashboardWrapper />
              </SignedIn>
              <SignedOut>
                 <Navigate to="/login" replace />
              </SignedOut>
            </>
          }
        />
        <Route 
          path="/login" 
          element={
            <>
              <SignedIn>
                <Navigate to="/" replace />
              </SignedIn>
              <SignedOut>
                <Login />
              </SignedOut>
            </>
          } 
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App;