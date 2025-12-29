import React, { useState } from 'react'
import ChatInterface from './components/ChatInterface'
import InfoPanel from './components/InfoPanel'
import { X } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

function App() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  return (
    // Mobile: h-screen, p-0. Desktop: min-h-screen, p-4
    <div className="h-screen md:min-h-screen bg-gradient-to-br from-indigo-100 via-sky-50 to-emerald-50 flex items-center justify-center p-0 md:p-4">

      {/* Mobile: h-full, rounded-none. Desktop: h-[85vh], rounded-3xl */}
      <div className="w-full max-w-5xl h-full md:h-[85vh] flex flex-col md:flex-row gap-6 relative">

        {/* Desktop Sidebar */}
        <div className="hidden md:flex flex-col w-1/3 glass rounded-3xl p-8">
          <InfoPanel />
        </div>

        {/* Mobile Slide-out Drawer */}
        <AnimatePresence>
          {isMobileMenuOpen && (
            <>
              {/* Backdrop */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                onClick={() => setIsMobileMenuOpen(false)}
                className="absolute inset-0 bg-slate-900/20 backdrop-blur-sm z-40 md:hidden"
              />

              {/* Drawer */}
              <motion.div
                initial={{ x: '-100%' }}
                animate={{ x: 0 }}
                exit={{ x: '-100%' }}
                transition={{ type: "spring", stiffness: 300, damping: 30 }}
                className="absolute left-0 top-0 bottom-0 w-[80%] max-w-sm bg-white shadow-2xl z-50 p-6 md:hidden"
              >
                <button
                  onClick={() => setIsMobileMenuOpen(false)}
                  className="absolute top-4 right-4 p-2 text-slate-400 hover:text-slate-600"
                >
                  <X size={24} />
                </button>
                <div className="mt-8 h-full">
                  <InfoPanel />
                </div>
              </motion.div>
            </>
          )}
        </AnimatePresence>

        {/* Chat Area */}
        {/* Mobile: rounded-none. Desktop: rounded-3xl */}
        <div className="flex-1 glass md:rounded-3xl rounded-none overflow-hidden shadow-2xl relative flex flex-col">
          <ChatInterface onMenuClick={() => setIsMobileMenuOpen(true)} />
        </div>

      </div>
    </div>
  )
}

export default App
