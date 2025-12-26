import React, { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, User, Bot, Loader2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';

const MessageBubble = ({ message }) => {
    const isBot = message.sender === 'bot';

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className={`flex w-full mb-6 ${isBot ? 'justify-start' : 'justify-end'}`}
        >
            <div className={`flex max-w-[85%] md:max-w-[75%] gap-3 ${isBot ? 'flex-row' : 'flex-row-reverse'}`}>

                {/* Avatar */}
                <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 mt-1 shadow-sm
          ${isBot ? 'bg-gradient-to-tr from-sky-500 to-emerald-400 text-white' : 'bg-slate-200 text-slate-500'}`}>
                    {isBot ? <Bot size={18} /> : <User size={18} />}
                </div>

                {/* Bubble */}
                <div className={`p-4 rounded-2xl shadow-sm text-sm leading-relaxed
          ${isBot
                        ? 'bg-white text-slate-700 rounded-tl-none border border-slate-100'
                        : 'bg-gradient-to-r from-sky-600 to-indigo-600 text-white rounded-tr-none'
                    }`}>
                    {isBot ? (
                        <ReactMarkdown className="prose prose-sm max-w-none prose-p:my-1 prose-headings:text-slate-800 prose-a:text-sky-600">
                            {message.text}
                        </ReactMarkdown>
                    ) : (
                        <p>{message.text}</p>
                    )}
                </div>
            </div>
        </motion.div>
    );
};

const ChatInterface = () => {
    const [input, setInput] = useState('');
    const [messages, setMessages] = useState([
        { id: 1, text: "Hello! I'm the Otic Foundation AI. How can I help you today?", sender: 'bot' }
    ]);
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = async (e) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMsg = { id: Date.now(), text: input, sender: 'user' };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setIsLoading(true);

        // Create a placeholder bot message
        const botMsgId = Date.now() + 1;
        setMessages(prev => [...prev, { id: botMsgId, text: '', sender: 'bot' }]);

        try {
            const response = await fetch('http://localhost:8000/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: userMsg.text })
            });

            if (!response.ok) throw new Error('Network response was not ok');

            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const text = decoder.decode(value);
                setMessages(prev => prev.map(msg =>
                    msg.id === botMsgId
                        ? { ...msg, text: msg.text + text }
                        : msg
                ));
            }

        } catch (error) {
            console.error("Error sending message:", error);
            setMessages(prev => prev.map(msg =>
                msg.id === botMsgId
                    ? { ...msg, text: "I'm having trouble connecting to the server. Please ensure the backend is running and Ollama is started.", isError: true }
                    : msg
            ));
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-full bg-slate-50/50">

            {/* Header (Mobile only) */}
            <div className="md:hidden p-4 border-b border-white/20 bg-white/40 backdrop-blur-sm flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-sky-500 to-emerald-400 flex items-center justify-center text-white font-bold text-sm">
                    O
                </div>
                <span className="font-semibold text-slate-800">Otic AI</span>
            </div>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-4 md:p-6 scroll-smooth">
                <AnimatePresence>
                    {messages.map((msg) => (
                        <MessageBubble key={msg.id} message={msg} />
                    ))}
                </AnimatePresence>

                {isLoading && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="flex w-full mb-6 justify-start"
                    >
                        <div className="flex gap-3">
                            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-sky-500 to-emerald-400 flex items-center justify-center text-white shadow-sm mt-1">
                                <Bot size={18} />
                            </div>
                            <div className="p-4 bg-white rounded-2xl rounded-tl-none border border-slate-100 flex items-center gap-2 text-slate-400 text-sm shadow-sm">
                                <Loader2 className="animate-spin" size={16} />
                                <span>Thinking...</span>
                            </div>
                        </div>
                    </motion.div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-4 md:p-6 bg-white/60 backdrop-blur-md border-t border-white/50">
                <form onSubmit={handleSend} className="relative flex items-center max-w-3xl mx-auto">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Ask about Otic Foundation..."
                        className="w-full bg-white border border-slate-200 text-slate-800 placeholder-slate-400 pl-4 pr-14 py-4 rounded-xl focus:outline-none focus:ring-2 focus:ring-sky-500/50 focus:border-sky-500 shadow-sm transition-all"
                        disabled={isLoading}
                    />
                    <button
                        type="submit"
                        disabled={isLoading || !input.trim()}
                        className="absolute right-2 p-2 bg-gradient-to-r from-sky-500 to-emerald-500 text-white rounded-lg hover:shadow-lg disabled:opacity-50 disabled:shadow-none transition-all"
                    >
                        {isLoading ? <Loader2 className="animate-spin" size={20} /> : <Send size={20} />}
                    </button>
                </form>
                <div className="text-center mt-2">
                    <p className="text-[10px] text-slate-400 uppercase tracking-widest font-medium">Powered by Otic Intelligence</p>
                </div>
            </div>

        </div>
    );
};

export default ChatInterface;
