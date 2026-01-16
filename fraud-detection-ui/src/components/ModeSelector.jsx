import React from 'react';

function ModeSelector({ mode, setMode }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
      <button
        onClick={() => setMode('banking')}
        className={`group relative overflow-hidden py-10 px-6 rounded-3xl font-bold text-xl transition-all duration-300 transform hover:scale-105 ${mode === 'banking'
            ? 'bg-gradient-to-br from-cyan-500/30 to-blue-600/30 border-2 border-cyan-400 shadow-xl shadow-cyan-500/50'
            : 'bg-gradient-to-br from-slate-800/50 to-slate-900/50 border-2 border-slate-700 hover:border-cyan-400/50'
          }`}
      >
        {/* Circuit Pattern Background */}
        <div className="absolute inset-0 opacity-10">
          <svg className="w-full h-full">
            <defs>
              <pattern id="circuit-banking" x="0" y="0" width="40" height="40" patternUnits="userSpaceOnUse">
                <circle cx="5" cy="5" r="2" fill="currentColor" />
                <line x1="5" y1="5" x2="20" y2="5" stroke="currentColor" strokeWidth="1" />
                <line x1="20" y1="5" x2="20" y2="20" stroke="currentColor" strokeWidth="1" />
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#circuit-banking)" />
          </svg>
        </div>

        {/* Glow Effect */}
        {mode === 'banking' && (
          <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/20 to-blue-500/20 animate-pulse"></div>
        )}

        <div className="relative z-10">
          <div className="text-6xl mb-4 transform group-hover:scale-110 transition-transform">🏦</div>
          <div className={`text-2xl font-black ${mode === 'banking' ? 'text-cyan-300' : 'text-slate-400'}`}>
            Banking Fraud
          </div>
          <p className={`text-sm mt-2 ${mode === 'banking' ? 'text-cyan-400/80' : 'text-slate-500'}`}>
            Raw transaction analysis
          </p>
        </div>

        {/* Corner Accent */}
        <div className={`absolute top-0 right-0 w-20 h-20 ${mode === 'banking' ? 'bg-cyan-500/20' : 'bg-slate-700/20'} rounded-bl-full`}></div>
      </button>

      <button
        onClick={() => setMode('credit_card')}
        className={`group relative overflow-hidden py-10 px-6 rounded-3xl font-bold text-xl transition-all duration-300 transform hover:scale-105 ${mode === 'credit_card'
            ? 'bg-gradient-to-br from-purple-500/30 to-pink-600/30 border-2 border-purple-400 shadow-xl shadow-purple-500/50'
            : 'bg-gradient-to-br from-slate-800/50 to-slate-900/50 border-2 border-slate-700 hover:border-purple-400/50'
          }`}
      >
        {/* Circuit Pattern Background */}
        <div className="absolute inset-0 opacity-10">
          <svg className="w-full h-full">
            <defs>
              <pattern id="circuit-credit" x="0" y="0" width="40" height="40" patternUnits="userSpaceOnUse">
                <circle cx="5" cy="5" r="2" fill="currentColor" />
                <line x1="5" y1="5" x2="20" y2="5" stroke="currentColor" strokeWidth="1" />
                <line x1="20" y1="5" x2="20" y2="20" stroke="currentColor" strokeWidth="1" />
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#circuit-credit)" />
          </svg>
        </div>

        {/* Glow Effect */}
        {mode === 'credit_card' && (
          <div className="absolute inset-0 bg-gradient-to-r from-purple-500/20 to-pink-500/20 animate-pulse"></div>
        )}

        <div className="relative z-10">
          <div className="text-6xl mb-4 transform group-hover:scale-110 transition-transform">💳</div>
          <div className={`text-2xl font-black ${mode === 'credit_card' ? 'text-purple-300' : 'text-slate-400'}`}>
            Credit Card Fraud
          </div>
          <p className={`text-sm mt-2 ${mode === 'credit_card' ? 'text-purple-400/80' : 'text-slate-500'}`}>
            PCA feature detection
          </p>
        </div>

        {/* Corner Accent */}
        <div className={`absolute top-0 right-0 w-20 h-20 ${mode === 'credit_card' ? 'bg-purple-500/20' : 'bg-slate-700/20'} rounded-bl-full`}></div>
      </button>
    </div>
  );
}

export default ModeSelector;