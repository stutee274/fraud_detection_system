import React, { useState } from 'react';
import { UserButton, useClerk } from '@clerk/clerk-react';

function Navbar({ user }) {
  const [showMenu, setShowMenu] = useState(false);
  const [showLogoutModal, setShowLogoutModal] = useState(false);
  const { signOut } = useClerk();

  const handleLogoutClick = () => {
    setShowLogoutModal(true);
  };

  const confirmLogout = () => {
    signOut();
    setShowLogoutModal(false);
  };

  return (
    <>
      <nav className="bg-gradient-to-r from-slate-950 via-slate-900 to-slate-950 shadow-2xl border-b-2 border-cyan-500/30 backdrop-blur-md relative overflow-hidden">
        {/* Animated Background Effect */}
        <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/5 via-purple-500/5 to-pink-500/5 animate-pulse"></div>

        {/* Glowing Line */}
        <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-cyan-500 to-transparent"></div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="flex justify-between items-center h-20">
            {/* Logo Section */}
            <div className="flex items-center space-x-4">
              <div className="relative group">
                <div className="absolute inset-0 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-2xl blur-lg opacity-50 group-hover:opacity-75 transition-opacity"></div>
                <div className="relative bg-gradient-to-br from-cyan-500 to-blue-600 p-3 rounded-2xl shadow-lg transform hover:scale-110 transition-transform duration-200">
                  <span className="text-3xl font-black text-white">FD</span>
                </div>
              </div>
              <div>
                <h1 className="text-2xl font-black bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-400 bg-clip-text text-transparent">
                  Fraud Detector
                </h1>
                <p className="text-xs text-cyan-400/80 font-medium">
                  Security Platform For Banking Transactions
                </p>
              </div>
            </div>

            {/* User Section */}
            <div className="flex items-center space-x-6">
              {/* Notifications Badge */}
              <button className="relative p-2 text-cyan-400 hover:text-cyan-300 transition-colors group">
                <div className="absolute inset-0 bg-cyan-500/20 rounded-lg blur-md opacity-0 group-hover:opacity-100 transition-opacity"></div>
                <svg className="w-6 h-6 relative z-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                </svg>
                <span className="absolute top-0 right-0 block h-2 w-2 rounded-full bg-red-500 ring-2 ring-slate-900 animate-pulse"></span>
              </button>

              {/* User Info */}
              <div className="flex items-center space-x-3">
                <div className="text-right hidden sm:block">
                  <p className="text-sm font-bold text-cyan-300">
                    {user?.fullName || user?.firstName || 'User'}
                  </p>
                  <p className="text-xs text-cyan-500/70">
                    {user?.primaryEmailAddress?.emailAddress?.substring(0, 20)}
                    {user?.primaryEmailAddress?.emailAddress?.length > 20 ? '...' : ''}
                  </p>
                </div>

                {/* Clerk User Button */}
                <div className="relative group">
                  <div className="absolute inset-0 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl blur-md opacity-50 group-hover:opacity-75 transition-opacity"></div>
                  <UserButton
                    afterSignOutUrl="/"
                    appearance={{
                      elements: {
                        avatarBox: "w-12 h-12 rounded-xl ring-2 ring-purple-500 hover:ring-cyan-400 transition-all duration-200 relative z-10",
                        userButtonPopoverCard: "shadow-2xl rounded-2xl bg-slate-900 border border-cyan-500/30",
                        userButtonPopoverActionButton: "hover:bg-cyan-500/10 text-cyan-300",
                        userButtonPopoverActionButtonText: "text-cyan-300 font-medium",
                        userButtonPopoverFooter: "hidden"
                      }
                    }}
                  />
                </div>

                {/* Logout Button */}
                <button
                  onClick={handleLogoutClick}
                  className="hidden sm:flex items-center space-x-2 bg-gradient-to-r from-red-600 to-pink-600 text-white px-5 py-2.5 rounded-xl hover:from-red-700 hover:to-pink-700 transition-all duration-200 font-bold shadow-lg shadow-red-500/30 hover:shadow-red-500/50 border border-red-400/30 group"
                >
                  <svg className="w-5 h-5 group-hover:rotate-12 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                  </svg>
                  <span>Logout</span>
                </button>
              </div>

              {/* Mobile Menu Button */}
              <button
                onClick={() => setShowMenu(!showMenu)}
                className="sm:hidden p-2 rounded-lg bg-slate-800/50 border border-cyan-500/30 hover:bg-slate-700/50 transition-colors"
              >
                <svg className="w-6 h-6 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Menu */}
        {showMenu && (
          <div className="sm:hidden bg-slate-900/95 backdrop-blur-md border-t border-cyan-500/30 py-4 px-4 animate-slideDown">
            <div className="space-y-3">
              <div className="flex items-center space-x-3 p-4 rounded-xl bg-gradient-to-br from-slate-800/80 to-slate-900/80 border border-cyan-500/20">
                <div className="flex-1">
                  <p className="text-sm font-bold text-cyan-300">
                    {user?.fullName || user?.firstName || 'User'}
                  </p>
                  <p className="text-xs text-cyan-500/70">
                    {user?.primaryEmailAddress?.emailAddress}
                  </p>
                </div>
              </div>
              <button
                onClick={handleLogoutClick}
                className="w-full text-left p-4 rounded-xl bg-gradient-to-r from-red-600 to-pink-600 text-white hover:from-red-700 hover:to-pink-700 font-bold shadow-lg shadow-red-500/30 border border-red-400/30"
              >
                Logout
              </button>
            </div>
          </div>
        )}
      </nav>

      {/* Logout Confirmation Modal */}
      {showLogoutModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4 animate-fadeIn">
          <div className="bg-gradient-to-br from-slate-900 to-slate-800 border-2 border-cyan-500/30 rounded-3xl p-10 max-w-md w-full shadow-2xl shadow-cyan-500/20 transform animate-slideUp">
            <div className="text-center mb-8">
              <div className="mx-auto w-24 h-24 bg-gradient-to-br from-red-500 to-pink-600 rounded-full flex items-center justify-center mb-6 relative">
                <div className="absolute inset-0 bg-gradient-to-br from-red-500 to-pink-600 rounded-full blur-xl opacity-50 animate-pulse"></div>
                <svg className="w-12 h-12 text-white relative z-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
              </div>
              <h2 className="text-4xl font-black text-cyan-300 mb-3">
                Confirm Logout
              </h2>
              <p className="text-cyan-400 text-lg mb-2">
                Are you sure you want to logout from Fraud Detector?
              </p>
              <p className="text-sm text-cyan-500/70">
                You can always sign back in anytime
              </p>
            </div>

            <div className="flex flex-col sm:flex-row gap-4">
              <button
                onClick={() => setShowLogoutModal(false)}
                className="flex-1 bg-slate-700 text-slate-300 py-4 px-6 rounded-xl font-bold hover:bg-slate-600 transition-all duration-200 border border-slate-600"
              >
                Cancel
              </button>
              <button
                onClick={confirmLogout}
                className="flex-1 bg-gradient-to-r from-red-500 to-pink-600 text-white py-4 px-6 rounded-xl font-bold hover:from-red-600 hover:to-pink-700 transition-all duration-200 shadow-lg shadow-red-500/30 hover:shadow-red-500/50 border border-red-400/30"
              >
                Yes, Logout
              </button>
            </div>
          </div>
        </div>
      )}

      <style jsx>{`
        @keyframes slideUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

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

        @keyframes fadeIn {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }

        .animate-slideUp {
          animation: slideUp 0.3s ease-out;
        }

        .animate-slideDown {
          animation: slideDown 0.3s ease-out;
        }

        .animate-fadeIn {
          animation: fadeIn 0.3s ease-out;
        }
      `}</style>
    </>
  );
}

export default Navbar;