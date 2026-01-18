"use client";

import { Product } from "@/lib/mockData";
import { Button } from "@/components/ui/button";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogDescription,
} from "@/components/ui/dialog";
import { motion } from "framer-motion";
import { CheckCircle2, Package, Sparkles } from "lucide-react";
import Image from "next/image";

interface CheckoutProps {
    isOpen: boolean;
    onClose: () => void;
    items: Product[];
    onConfirm: () => void;
    isLoading?: boolean;
}

export function Checkout({ isOpen, onClose, items, onConfirm, isLoading = false }: CheckoutProps) {
    const total = items.reduce((sum, item) => sum + item.price, 0);

    return (
        <Dialog open={isOpen} onOpenChange={onClose}>
            <DialogContent className="sm:max-w-md glass-card border-white/10 bg-[#0a0a0f]/95">
                <DialogHeader>
                    <DialogTitle className="flex items-center gap-2 text-white">
                        <div className="p-2 rounded-lg bg-primary/20">
                            <Package className="h-5 w-5 text-primary" />
                        </div>
                        Order Summary
                    </DialogTitle>
                    <DialogDescription className="text-muted-foreground">
                        Review your order before completing purchase
                    </DialogDescription>
                </DialogHeader>

                <div className="space-y-4 py-4">
                    {/* Items */}
                    <div className="space-y-3 max-h-60 overflow-y-auto">
                        {items.map((item) => (
                            <div
                                key={item.id}
                                className="flex items-center gap-3 p-2 rounded-lg glass"
                            >
                                <div className="relative h-12 w-12 rounded-lg overflow-hidden flex-shrink-0">
                                    <Image
                                        src={item.image}
                                        alt={item.name}
                                        fill
                                        className="object-cover"
                                        unoptimized
                                    />
                                </div>
                                <div className="flex-1 min-w-0">
                                    <p className="text-sm font-medium text-white line-clamp-1">{item.name}</p>
                                    <p className="text-xs text-muted-foreground">{item.store}</p>
                                </div>
                                <span className="text-primary font-medium">${item.price.toFixed(2)}</span>
                            </div>
                        ))}
                    </div>

                    {/* Total */}
                    <div className="border-t border-white/10 pt-4">
                        <div className="flex justify-between items-center">
                            <span className="text-muted-foreground">Total</span>
                            <span className="text-2xl font-bold text-white">${total.toFixed(2)}</span>
                        </div>
                    </div>
                </div>

                {/* Actions */}
                <div className="flex gap-3">
                    <Button
                        variant="outline"
                        onClick={onClose}
                        disabled={isLoading}
                        className="flex-1 border-white/10 hover:bg-white/5"
                    >
                        Cancel
                    </Button>
                    <Button
                        onClick={onConfirm}
                        disabled={isLoading}
                        className="flex-1 bg-primary hover:bg-primary/90 hover:glow-primary gap-2"
                    >
                        {isLoading ? (
                            <div className="h-4 w-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                        ) : (
                            <CheckCircle2 className="h-4 w-4" />
                        )}
                        {isLoading ? "Processing..." : "Confirm"}
                    </Button>
                </div>
            </DialogContent>
        </Dialog>
    );
}

export interface CheckoutResponse {
    store: string;
    checkout_url: string;
    item_count: number;
    error?: string;
}

interface OrderSuccessProps {
    isOpen: boolean;
    onClose: () => void;
    checkouts: CheckoutResponse[];
}

export function OrderSuccess({ isOpen, onClose, checkouts }: OrderSuccessProps) {
    return (
        <Dialog open={isOpen} onOpenChange={onClose}>
            <DialogContent className="sm:max-w-md glass-card border-white/10 bg-[#0a0a0f]/95 text-center">
                <motion.div
                    initial={{ scale: 0.8, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    className="flex flex-col items-center gap-6 py-8"
                >
                    {/* Success Icon */}
                    <div className="relative">
                        <div className="h-24 w-24 rounded-full bg-primary/20 flex items-center justify-center glow-primary">
                            <CheckCircle2 className="h-12 w-12 text-primary" />
                        </div>
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: 0.4 }}
                            className="absolute -top-2 -right-2"
                        >
                            <Sparkles className="h-8 w-8 text-accent" />
                        </motion.div>
                    </div>

                    {/* Text */}
                    <div>
                        <h2 className="text-2xl font-bold text-white">Ready to Checkout!</h2>
                        <p className="text-muted-foreground mt-2">
                            We've prepared your carts. Please complete your purchase at each store:
                        </p>
                    </div>

                    {/* Checkout Links */}
                    <div className="w-full space-y-3 mt-2">
                        {checkouts.map((checkout, idx) => (
                            <div key={idx} className="glass p-3 rounded-xl flex items-center justify-between">
                                <div className="text-left">
                                    <p className="text-sm font-medium text-white">{checkout.store}</p>
                                    <p className="text-xs text-muted-foreground">{checkout.item_count} items</p>
                                    {checkout.error && <p className="text-xs text-red-400 max-w-[200px] truncate">{checkout.error}</p>}
                                </div>
                                {checkout.checkout_url && (
                                    <Button
                                        size="sm"
                                        className="bg-primary text-xs"
                                        onClick={() => window.open(checkout.checkout_url, '_blank')}
                                    >
                                        Pay Now
                                    </Button>
                                )}
                            </div>
                        ))}
                    </div>

                    {/* Button */}
                    <Button
                        onClick={onClose}
                        variant="ghost"
                        className="mt-2 text-muted-foreground hover:text-white"
                    >
                        Continue Shopping
                    </Button>
                </motion.div>
            </DialogContent>
        </Dialog>
    );
}
