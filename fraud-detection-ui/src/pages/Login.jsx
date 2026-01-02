// import React, { useState } from 'react';

// function Login({ onLogin }) {
//   const [email, setEmail] = useState('');
//   const [password, setPassword] = useState('');

//   const handleSubmit = (e) => {
//     e.preventDefault();
    
//     if (email && password) {
//       onLogin({
//         name: email.split('@')[0],
//         email: email,
//         loginMethod: 'email'
//       });
//     } else {
//       alert('Please enter email and password');
//     }
//   };

//   const handleGoogleLogin = () => {
//     // Simulate Google login
//     onLogin({
//       name: 'Google User',
//       email: 'user@gmail.com',
//       picture: 'https://via.placeholder.com/150',
//       loginMethod: 'google'
//     });
//   };

//   return (
//     <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-500 to-purple-600">
//       <div className="bg-white p-8 rounded-2xl shadow-2xl w-96">
//         <div className="text-center mb-8">
//           <div className="text-6xl mb-4">🛡️</div>
//           <h1 className="text-3xl font-bold text-gray-900">Fraud Detector</h1>
//           <p className="text-gray-600 mt-2">Login to your account</p>
//         </div>

//         <form onSubmit={handleSubmit} className="space-y-4">
//           <div>
//             <label className="block text-sm font-medium text-gray-700 mb-2">
//               Email
//             </label>
//             <input
//               type="email"
//               value={email}
//               onChange={(e) => setEmail(e.target.value)}
//               className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
//               placeholder="your@email.com"
//             />
//           </div>

//           <div>
//             <label className="block text-sm font-medium text-gray-700 mb-2">
//               Password
//             </label>
//             <input
//               type="password"
//               value={password}
//               onChange={(e) => setPassword(e.target.value)}
//               className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
//               placeholder="••••••••"
//             />
//           </div>

//           <button
//             type="submit"
//             className="w-full bg-primary text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition"
//           >
//             Login
//           </button>
//         </form>

//         <div className="mt-6">
//           <div className="relative">
//             <div className="absolute inset-0 flex items-center">
//               <div className="w-full border-t border-gray-300"></div>
//             </div>
//             <div className="relative flex justify-center text-sm">
//               <span className="px-2 bg-white text-gray-500">Or continue with</span>
//             </div>
//           </div>

//           <button
//             onClick={handleGoogleLogin}
//             className="mt-4 w-full bg-white border border-gray-300 text-gray-700 py-3 rounded-lg font-semibold hover:bg-gray-50 transition flex items-center justify-center"
//           >
//             <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
//               <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
//               <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
//               <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
//               <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
//             </svg>
//             Sign in with Google
//           </button>
//         </div>

//         <p className="mt-4 text-center text-xs text-gray-500">
//           Demo: Use any email/password or click Google sign in
//         </p>
//       </div>
//     </div>
//   );
// }


// export default Login;

import React, { useState } from 'react';
import { SignIn, SignUp } from '@clerk/clerk-react';

function Login() {
  const [activeTab, setActiveTab] = useState('signin');

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-600 p-4 relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-500 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-pink-500 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-2000"></div>
        <div className="absolute top-1/2 left-1/2 w-80 h-80 bg-indigo-500 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-4000"></div>
      </div>

      {/* Main content */}
      <div className="relative z-10 w-full max-w-md">
        {/* Header Section */}
        <div className="text-center mb-8 transform hover:scale-105 transition-transform duration-300">
          <div className="inline-block bg-white rounded-full p-6 shadow-2xl mb-4">
            <span className="text-7xl">🛡️</span>
          </div>
          <h1 className="text-5xl font-extrabold text-white mb-3 drop-shadow-lg">
            Fraud Detector
          </h1>
          <p className="text-xl text-purple-100 font-medium">
            AI-Powered Transaction Security
          </p>
          <div className="flex justify-center space-x-2 mt-4">
            <span className="px-4 py-1 bg-white/20 backdrop-blur-sm rounded-full text-white text-sm font-semibold">
              🔒 Secure
            </span>
            <span className="px-4 py-1 bg-white/20 backdrop-blur-sm rounded-full text-white text-sm font-semibold">
              ⚡ Fast
            </span>
            <span className="px-4 py-1 bg-white/20 backdrop-blur-sm rounded-full text-white text-sm font-semibold">
              🤖 AI-Powered
            </span>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex mb-6 bg-white/10 backdrop-blur-md rounded-2xl p-2">
          <button
            onClick={() => setActiveTab('signin')}
            className={`flex-1 py-3 px-6 rounded-xl font-bold transition-all duration-200 ${
              activeTab === 'signin'
                ? 'bg-white text-purple-600 shadow-lg'
                : 'text-white hover:bg-white/10'
            }`}
          >
            Sign In
          </button>
          <button
            onClick={() => setActiveTab('signup')}
            className={`flex-1 py-3 px-6 rounded-xl font-bold transition-all duration-200 ${
              activeTab === 'signup'
                ? 'bg-white text-purple-600 shadow-lg'
                : 'text-white hover:bg-white/10'
            }`}
          >
            Sign Up
          </button>
        </div>

        {/* Auth Forms */}
        <div className="bg-white rounded-3xl shadow-2xl p-8 backdrop-blur-sm border border-white/20">
          {activeTab === 'signin' ? (
            <SignIn 
              appearance={{
                elements: {
                  rootBox: "w-full",
                  card: "shadow-none bg-transparent",
                  headerTitle: "text-2xl font-bold text-gray-800",
                  headerSubtitle: "text-gray-600",
                  socialButtonsBlockButton: "bg-white border-2 border-gray-200 hover:border-purple-500 hover:bg-purple-50 transition-all duration-200 flex items-center justify-center space-x-2",
                  socialButtonsBlockButtonText: "font-semibold",
                  formButtonPrimary: "bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-bold py-3 rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl",
                  footerActionLink: "text-purple-600 hover:text-purple-800 font-semibold",
                  formFieldInput: "border-2 border-gray-200 focus:border-purple-500 rounded-xl py-3 px-4 transition-all duration-200",
                  formFieldLabel: "text-gray-700 font-semibold mb-2",
                  dividerLine: "bg-gray-200",
                  dividerText: "text-gray-500 font-medium",
                  identityPreviewText: "text-gray-700",
                  identityPreviewEditButton: "text-purple-600 hover:text-purple-800",
                  formResendCodeLink: "text-purple-600 hover:text-purple-800",
                  otpCodeFieldInput: "border-2 border-gray-200 focus:border-purple-500 rounded-xl"
                },
                layout: {
                  socialButtonsPlacement: "top",
                  socialButtonsVariant: "blockButton",
                  showOptionalFields: true
                }
              }}
              routing="hash"
              signUpUrl="#/sign-up"
              afterSignInUrl="/"
            />
          ) : (
            <SignUp 
              appearance={{
                elements: {
                  rootBox: "w-full",
                  card: "shadow-none bg-transparent",
                  headerTitle: "text-2xl font-bold text-gray-800",
                  headerSubtitle: "text-gray-600",
                  socialButtonsBlockButton: "bg-white border-2 border-gray-200 hover:border-purple-500 hover:bg-purple-50 transition-all duration-200 flex items-center justify-center space-x-2",
                  socialButtonsBlockButtonText: "font-semibold",
                  formButtonPrimary: "bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-bold py-3 rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl",
                  footerActionLink: "text-purple-600 hover:text-purple-800 font-semibold",
                  formFieldInput: "border-2 border-gray-200 focus:border-purple-500 rounded-xl py-3 px-4 transition-all duration-200",
                  formFieldLabel: "text-gray-700 font-semibold mb-2",
                  dividerLine: "bg-gray-200",
                  dividerText: "text-gray-500 font-medium",
                  formFieldInputShowPasswordButton: "text-purple-600 hover:text-purple-800",
                  identityPreviewText: "text-gray-700",
                  identityPreviewEditButton: "text-purple-600 hover:text-purple-800",
                  formResendCodeLink: "text-purple-600 hover:text-purple-800",
                  otpCodeFieldInput: "border-2 border-gray-200 focus:border-purple-500 rounded-xl"
                },
                layout: {
                  socialButtonsPlacement: "top",
                  socialButtonsVariant: "blockButton",
                  showOptionalFields: true
                }
              }}
              routing="hash"
              signInUrl="#/sign-in"
              afterSignUpUrl="/"
            />
          )}
        </div>

        {/* Features */}
        <div className="mt-8 grid grid-cols-3 gap-4 text-center">
          <div className="bg-white/10 backdrop-blur-md rounded-2xl p-4 border border-white/20 hover:bg-white/20 transition-all duration-200">
            <div className="text-3xl mb-2">🏦</div>
            <p className="text-white text-sm font-semibold">Banking</p>
          </div>
          <div className="bg-white/10 backdrop-blur-md rounded-2xl p-4 border border-white/20 hover:bg-white/20 transition-all duration-200">
            <div className="text-3xl mb-2">💳</div>
            <p className="text-white text-sm font-semibold">Credit Card</p>
          </div>
          <div className="bg-white/10 backdrop-blur-md rounded-2xl p-4 border border-white/20 hover:bg-white/20 transition-all duration-200">
            <div className="text-3xl mb-2">📊</div>
            <p className="text-white text-sm font-semibold">Analytics</p>
          </div>
        </div>

        {/* Footer */}
        <p className="text-center text-purple-100 text-sm mt-8">
          Protected by enterprise-grade security 🔐
        </p>
      </div>

      {/* CSS for animations */}
      <style jsx>{`
        @keyframes blob {
          0%, 100% { transform: translate(0, 0) scale(1); }
          25% { transform: translate(20px, -50px) scale(1.1); }
          50% { transform: translate(-20px, 20px) scale(0.9); }
          75% { transform: translate(50px, 50px) scale(1.05); }
        }
        
        .animate-blob {
          animation: blob 7s infinite;
        }
        
        .animation-delay-2000 {
          animation-delay: 2s;
        }
        
        .animation-delay-4000 {
          animation-delay: 4s;
        }
      `}</style>
    </div>
  );
}

export default Login;