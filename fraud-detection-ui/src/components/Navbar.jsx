// import React, { useState } from 'react';

// function Navbar({ user, onLogout }) {
//   const [showLogoutModal, setShowLogoutModal] = useState(false);

//   const handleLogoutClick = () => {
//     setShowLogoutModal(true);
//   };

//   const confirmLogout = () => {
//     setShowLogoutModal(false);
//     onLogout();
//   };

//   return (
//     <>
//       <nav className="bg-white shadow-md">
//         <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
//           <div className="flex justify-between items-center h-16">
//             <div className="flex items-center">
//               <span className="text-3xl">🛡️</span>
//               <span className="ml-3 text-xl font-bold text-primary">
//                 Fraud Detector
//               </span>
//             </div>
            
//             <div className="flex items-center space-x-4">
//               {user && (
//                 <>
//                   <div className="flex items-center space-x-2">
//                     {user.picture ? (
//                       <img 
//                         src={user.picture} 
//                         alt={user.name}
//                         className="w-8 h-8 rounded-full"
//                       />
//                     ) : (
//                       <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center text-white font-bold">
//                         {user.name.charAt(0).toUpperCase()}
//                       </div>
//                     )}
//                     <span className="text-gray-700 font-medium">
//                       {user.name}
//                     </span>
//                   </div>
//                   <button
//                     onClick={handleLogoutClick}
//                     className="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition"
//                   >
//                     Logout
//                   </button>
//                 </>
//               )}
//             </div>
//           </div>
//         </div>
//       </nav>

//       {/* Logout Confirmation Modal */}
//       {showLogoutModal && (
//         <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
//           <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4 shadow-2xl">
//             <div className="text-center mb-6">
//               <div className="text-5xl mb-4">👋</div>
//               <h2 className="text-2xl font-bold text-gray-900 mb-2">
//                 Are you sure?
//               </h2>
//               <p className="text-gray-600">
//                 Do you want to logout from Fraud Detector?
//               </p>
//             </div>
            
//             <div className="flex space-x-4">
//               <button
//                 onClick={() => setShowLogoutModal(false)}
//                 className="flex-1 bg-gray-200 text-gray-700 py-3 px-6 rounded-lg font-semibold hover:bg-gray-300 transition"
//               >
//                 Cancel
//               </button>
//               <button
//                 onClick={confirmLogout}
//                 className="flex-1 bg-red-500 text-white py-3 px-6 rounded-lg font-semibold hover:bg-red-600 transition"
//               >
//                 Yes, Logout
//               </button>
//             </div>
//           </div>
//         </div>
//       )}
//     </>
//   );
// }

// export default Navbar;

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
      <nav className="bg-white shadow-lg border-b-4 border-gradient-to-r from-purple-500 to-pink-500">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-20">
            {/* Logo Section */}
            <div className="flex items-center space-x-4">
              <div className="bg-gradient-to-br from-purple-600 to-pink-600 p-3 rounded-2xl shadow-lg transform hover:scale-110 transition-transform duration-200">
                <span className="text-4xl">🛡️</span>
              </div>
              <div>
                <h1 className="text-2xl font-extrabold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                  Fraud Detector
                </h1>
                <p className="text-xs text-gray-500 font-medium">
                  AI-Powered Security Platform
                </p>
              </div>
            </div>
            
            {/* User Section */}
            <div className="flex items-center space-x-6">
              {/* Notifications Badge */}
              <button className="relative p-2 text-gray-600 hover:text-purple-600 transition-colors">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                </svg>
                <span className="absolute top-0 right-0 block h-2 w-2 rounded-full bg-red-500 ring-2 ring-white"></span>
              </button>

              {/* User Info */}
              <div className="flex items-center space-x-3">
                <div className="text-right hidden sm:block">
                  <p className="text-sm font-bold text-gray-800">
                    {user?.fullName || user?.firstName || 'User'}
                  </p>
                  <p className="text-xs text-gray-500">
                    {user?.primaryEmailAddress?.emailAddress?.substring(0, 20)}
                    {user?.primaryEmailAddress?.emailAddress?.length > 20 ? '...' : ''}
                  </p>
                </div>
                
                {/* Clerk User Button */}
                <UserButton 
                  afterSignOutUrl="/"
                  appearance={{
                    elements: {
                      avatarBox: "w-12 h-12 rounded-xl ring-2 ring-purple-500 hover:ring-4 transition-all duration-200",
                      userButtonPopoverCard: "shadow-2xl rounded-2xl",
                      userButtonPopoverActionButton: "hover:bg-purple-50",
                      userButtonPopoverActionButtonText: "text-gray-700 font-medium",
                      userButtonPopoverFooter: "hidden"
                    }
                  }}
                />

                {/* Additional Logout Button */}
                <button
                  onClick={handleLogoutClick}
                  className="hidden sm:flex items-center space-x-2 bg-red-500 text-white px-4 py-2 rounded-xl hover:bg-red-600 transition-all duration-200 font-semibold shadow-lg hover:shadow-xl"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                  </svg>
                  <span>Logout</span>
                </button>
              </div>

              {/* Mobile Menu Button */}
              <button 
                onClick={() => setShowMenu(!showMenu)}
                className="sm:hidden p-2 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <svg className="w-6 h-6 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Menu */}
        {showMenu && (
          <div className="sm:hidden bg-white border-t border-gray-200 py-4 px-4">
            <div className="space-y-3">
              <div className="flex items-center space-x-3 p-3 rounded-lg bg-purple-50">
                <div className="flex-1">
                  <p className="text-sm font-bold text-gray-800">
                    {user?.fullName || user?.firstName || 'User'}
                  </p>
                  <p className="text-xs text-gray-500">
                    {user?.primaryEmailAddress?.emailAddress}
                  </p>
                </div>
              </div>
              <button 
                onClick={handleLogoutClick}
                className="w-full text-left p-3 rounded-lg bg-red-500 text-white hover:bg-red-600 font-semibold"
              >
                Logout
              </button>
            </div>
          </div>
        )}
      </nav>

      {/* Logout Confirmation Modal */}
      {showLogoutModal && (
        <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-3xl p-8 max-w-md w-full shadow-2xl transform animate-slideUp">
            <div className="text-center mb-6">
              <div className="mx-auto w-20 h-20 bg-gradient-to-br from-red-500 to-pink-600 rounded-full flex items-center justify-center mb-4">
                <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
              </div>
              <h2 className="text-3xl font-bold text-gray-900 mb-2">
                Confirm Logout
              </h2>
              <p className="text-gray-600 text-lg">
                Are you sure you want to logout from Fraud Detector?
              </p>
              <p className="text-sm text-gray-500 mt-2">
                You can always sign back in anytime
              </p>
            </div>
            
            <div className="flex flex-col sm:flex-row gap-3">
              <button
                onClick={() => setShowLogoutModal(false)}
                className="flex-1 bg-gray-200 text-gray-700 py-4 px-6 rounded-xl font-bold hover:bg-gray-300 transition-all duration-200"
              >
                Cancel
              </button>
              <button
                onClick={confirmLogout}
                className="flex-1 bg-gradient-to-r from-red-500 to-pink-600 text-white py-4 px-6 rounded-xl font-bold hover:from-red-600 hover:to-pink-700 transition-all duration-200 shadow-lg hover:shadow-xl"
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
        
        .animate-slideUp {
          animation: slideUp 0.3s ease-out;
        }
      `}</style>
    </>
  );
}

export default Navbar;