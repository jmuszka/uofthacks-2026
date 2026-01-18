"use client";

import { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { motion } from "framer-motion";
import { Send, Bot, User } from "lucide-react";

interface Message {
    role: "user" | "agent";
    text: string;
}

interface SideBarChatProps {
    onSendMessage: (message: string) => void;
    isLoading?: boolean;
    initialQuery?: string;
}

export function SideBarChat({ onSendMessage, isLoading = false, initialQuery }: SideBarChatProps) {
    const [message, setMessage] = useState("");
    const [messages, setMessages] = useState<Message[]>([]);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Initialize chat with the user's first search query
    useEffect(() => {
        if (initialQuery && messages.length === 0) {
            setMessages([
                { role: "user", text: initialQuery },
                { role: "agent", text: `Searching for "${initialQuery}"...` }
            ]);
        }
    }, [initialQuery, messages.length]);

    // Handle incoming agent responses - REMOVED per user request
    // We now only show "Searching for..." immediately upon send
    /*
    useEffect(() => {
        if (agentResponse) {
            setMessages((prev) => {
                const lastMsg = prev[prev.length - 1];
                if (lastMsg?.role === "agent" && lastMsg.text === agentResponse) return prev;
                return [...prev, { role: "agent", text: agentResponse }];
            });
        }
    }, [agentResponse]);
    */

    // Auto-scroll to bottom
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        if (message.trim() && !isLoading) {
            const userMessage = message.trim();
            setMessages((prev) => [...prev, { role: "user", text: userMessage }]);
            setMessage("");

            // Add static "Searching for..." message
            setTimeout(() => {
                setMessages((prev) => [...prev, { role: "agent", text: `Searching for "${userMessage}"...` }]);
            }, 100);

            // Trigger search
            onSendMessage(userMessage);

            // Simulation removed - waiting for agentResponse prop update
        }
    };

    return (
        <div className="fixed top-0 bottom-0 left-0 z-40 w-80 glass border-r border-white/10 flex flex-col">
            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 pt-6">
                {messages.length === 0 ? (
                    <div className="text-center text-muted-foreground text-sm py-4">
                        Your conversation will appear here
                    </div>
                ) : (
                    messages.map((msg, idx) => (
                        <motion.div
                            key={idx}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className={`flex gap-2 ${msg.role === "user" ? "flex-row-reverse" : "flex-row"}`}
                        >
                            {/* Avatar */}
                            <div className={`flex-shrink-0 h-8 w-8 rounded-full flex items-center justify-center ${msg.role === "user"
                                ? "bg-accent/20"
                                : "bg-primary/20"
                                }`}>
                                {msg.role === "user" ? (
                                    <User className="h-4 w-4 text-accent" />
                                ) : (
                                    <Bot className="h-4 w-4 text-primary" />
                                )}
                            </div>

                            {/* Message bubble */}
                            <div
                                className={`max-w-[85%] px-4 py-3 rounded-2xl text-sm leading-relaxed ${msg.role === "user"
                                    ? "bg-accent text-white rounded-br-sm"
                                    : "glass rounded-bl-sm text-white"
                                    }`}
                            >
                                {msg.text}
                            </div>
                        </motion.div>
                    ))
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="p-4 border-t border-white/10 bg-black/20">
                <form onSubmit={handleSubmit} className="relative">
                    <input
                        type="text"
                        value={message}
                        onChange={(e) => setMessage(e.target.value)}
                        placeholder="Refine your search..."
                        className="w-full h-12 pl-4 pr-12 rounded-xl glass-input text-white placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
                    />
                    <Button
                        type="submit"
                        size="icon"
                        disabled={!message.trim() || isLoading}
                        className="absolute right-2 top-2 h-8 w-8 rounded-lg bg-primary hover:bg-primary/90 transition-all"
                    >
                        <Send className="h-4 w-4" />
                    </Button>
                </form>
            </div>
        </div>
    );
}
