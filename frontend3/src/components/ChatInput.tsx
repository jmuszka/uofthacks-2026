"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { motion } from "framer-motion";
import { Search, Loader2 } from "lucide-react";

interface ChatInputProps {
    onSearch: (query: string) => void;
    isLoading?: boolean;
}

export function ChatInput({ onSearch, isLoading = false }: ChatInputProps) {
    const [query, setQuery] = useState("");

    const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        if (query.trim() && !isLoading) {
            onSearch(query.trim());
        }
    };

    return (
        <motion.form
            onSubmit={handleSubmit}
            className="w-full max-w-2xl mx-auto"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
        >
            <div className="relative flex items-center gap-3">
                {/* Input Container */}
                <div className="relative flex-1">
                    <Search className="absolute left-5 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
                    <input
                        type="text"
                        placeholder="What would you like to shop for?"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        disabled={isLoading}
                        className="
              w-full h-14 pl-14 pr-6 
              glass-input rounded-full
              text-lg text-white placeholder:text-muted-foreground
              focus:outline-none focus:ring-2 focus:ring-primary/50
              transition-all duration-300
              disabled:opacity-50
            "
                    />
                </div>

                {/* Submit Button */}
                <Button
                    type="submit"
                    size="lg"
                    disabled={!query.trim() || isLoading}
                    className="
            h-14 px-8 rounded-full
            bg-primary text-primary-foreground
            hover:bg-primary/90 hover:glow-primary
            transition-all duration-300
            disabled:opacity-50
          "
                >
                    {isLoading ? (
                        <Loader2 className="h-5 w-5 animate-spin" />
                    ) : (
                        <span className="font-semibold">Search</span>
                    )}
                </Button>
            </div>
        </motion.form>
    );
}
