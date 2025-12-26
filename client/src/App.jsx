import React from 'react'
import ChatInterface from './components/ChatInterface'

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-100 via-sky-50 to-emerald-50 flex items-center justify-center p-4">
      <div className="w-full max-w-5xl h-[85vh] flex flex-col md:flex-row gap-6">

        {/* Sidebar / Info Panel */}
        <div className="hidden md:flex flex-col justify-between w-1/3 glass rounded-3xl p-8 text-slate-800">
          <div>
            <div className="flex items-center gap-3 mb-8">
              <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-sky-500 to-emerald-400 flex items-center justify-center text-white font-bold text-xl">
                O
              </div>
              <h1 className="text-2xl font-bold tracking-tight">Otic Foundation</h1>
            </div>

            <p className="text-slate-600 mb-6 leading-relaxed">
              Empowering Uganda through Artificial Intelligence.
              Ask me about our skilling initiatives, the AI in Every City campaign, or how we are shaping the future of work.
            </p>

            <div className="space-y-4">
              <div className="p-4 rounded-2xl bg-sky-50 border border-sky-100">
                <h3 className="font-semibold text-sky-800 text-sm mb-1">Mission</h3>
                <p className="text-xs text-sky-700">Democratizing AI knowledge & emerging technologies.</p>
              </div>
              <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-100">
                <h3 className="font-semibold text-emerald-800 text-sm mb-1">Vision 2030</h3>
                <p className="text-xs text-emerald-700">Raising 3 Million AI Talents in Uganda.</p>
              </div>
            </div>
          </div>

          <div className="text-xs text-slate-400 mt-8">
            © 2025 Otic Foundation. All rights reserved.
          </div>
        </div>

        {/* Chat Area */}
        <div className="flex-1 glass rounded-3xl overflow-hidden shadow-2xl relative">
          <ChatInterface />
        </div>

      </div>
    </div>
  )
}

export default App
