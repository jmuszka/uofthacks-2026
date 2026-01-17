"use client";

import { Product } from "@/lib/mockData";
import { Button } from "@/components/ui/button";
import {
    Sheet,
    SheetContent,
    SheetHeader,
    SheetTitle,
} from "@/components/ui/sheet";
import { ScrollArea } from "@/components/ui/scroll-area";
import { motion, AnimatePresence } from "framer-motion";
import { ShoppingCart, Trash2, X } from "lucide-react";
import Image from "next/image";

interface CartProps {
    isOpen: boolean;
    onClose: () => void;
    items: Product[];
    onRemoveItem: (productId: string) => void;
    onCheckout: () => void;
}

export function Cart({ isOpen, onClose, items, onRemoveItem, onCheckout }: CartProps) {
    const total = items.reduce((sum, item) => sum + item.price, 0);

    return (
        <Sheet open={isOpen} onOpenChange={onClose}>
            <SheetContent
                className="w-full sm:max-w-md flex flex-col border-l border-white/10 bg-[#0a0a0f]/95 backdrop-blur-xl"
            >
                <SheetHeader className="border-b border-white/10 pb-4">
                    <SheetTitle className="flex items-center gap-3 text-white">
                        <div className="p-2 rounded-lg bg-primary/20">
                            <ShoppingCart className="h-5 w-5 text-primary" />
                        </div>
                        Your Cart
                        <span className="ml-auto glass px-3 py-1 rounded-full text-sm font-normal text-muted-foreground">
                            {items.length} items
                        </span>
                    </SheetTitle>
                </SheetHeader>

                {items.length === 0 ? (
                    <div className="flex-1 flex flex-col items-center justify-center text-center gap-4">
                        <div className="p-6 rounded-full glass">
                            <ShoppingCart className="h-12 w-12 text-muted-foreground" />
                        </div>
                        <div>
                            <p className="font-medium text-white">Your cart is empty</p>
                            <p className="text-sm text-muted-foreground mt-1">
                                Add some products to get started!
                            </p>
                        </div>
                    </div>
                ) : (
                    <>
                        <ScrollArea className="flex-1 -mx-6 px-6 py-4">
                            <AnimatePresence>
                                <div className="space-y-3">
                                    {items.map((item, index) => (
                                        <motion.div
                                            key={item.id}
                                            initial={{ opacity: 0, x: 20 }}
                                            animate={{ opacity: 1, x: 0 }}
                                            exit={{ opacity: 0, x: -20 }}
                                            transition={{ delay: index * 0.05 }}
                                            className="flex gap-4 p-3 glass-card rounded-xl"
                                        >
                                            <div className="relative h-20 w-20 rounded-lg overflow-hidden flex-shrink-0">
                                                <Image
                                                    src={item.image}
                                                    alt={item.name}
                                                    fill
                                                    className="object-cover"
                                                    unoptimized
                                                />
                                            </div>
                                            <div className="flex-1 min-w-0">
                                                <h4 className="font-medium text-sm text-white line-clamp-1">
                                                    {item.name}
                                                </h4>
                                                <p className="text-xs text-muted-foreground mt-0.5">
                                                    {item.store}
                                                </p>
                                                <p className="text-primary font-semibold mt-2">
                                                    ${item.price.toFixed(2)}
                                                </p>
                                            </div>
                                            <Button
                                                variant="ghost"
                                                size="icon"
                                                className="h-8 w-8 text-muted-foreground hover:text-red-400 hover:bg-red-400/10"
                                                onClick={() => onRemoveItem(item.id)}
                                            >
                                                <Trash2 className="h-4 w-4" />
                                            </Button>
                                        </motion.div>
                                    ))}
                                </div>
                            </AnimatePresence>
                        </ScrollArea>

                        {/* Footer */}
                        <div className="border-t border-white/10 pt-4 space-y-4">
                            <div className="flex justify-between items-center">
                                <span className="text-muted-foreground">Total</span>
                                <span className="text-2xl font-bold text-white">
                                    ${total.toFixed(2)}
                                </span>
                            </div>
                            <Button
                                className="w-full h-12 text-lg bg-primary hover:bg-primary/90 hover:glow-primary transition-all"
                                size="lg"
                                onClick={onCheckout}
                            >
                                Checkout
                            </Button>
                        </div>
                    </>
                )}
            </SheetContent>
        </Sheet>
    );
}
