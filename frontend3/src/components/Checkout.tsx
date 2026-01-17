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
}

export function Checkout({ isOpen, onClose, items, onConfirm }: CheckoutProps) {
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
                        className="flex-1 border-white/10 hover:bg-white/5"
                    >
                        Cancel
                    </Button>
                    <Button
                        onClick={onConfirm}
                        className="flex-1 bg-primary hover:bg-primary/90 hover:glow-primary gap-2"
                    >
                        <CheckCircle2 className="h-4 w-4" />
                        Confirm
                    </Button>
                </div>
            </DialogContent>
        </Dialog>
    );
}

interface OrderSuccessProps {
    isOpen: boolean;
    onClose: () => void;
}

export function OrderSuccess({ isOpen, onClose }: OrderSuccessProps) {
    return (
        <Dialog open={isOpen} onOpenChange={onClose}>
            <DialogContent className="sm:max-w-md glass-card border-white/10 bg-[#0a0a0f]/95 text-center">
                <motion.div
                    initial={{ scale: 0.8, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    className="flex flex-col items-center gap-6 py-8"
                >
                    {/* Success Icon */}
                    <motion.div
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        transition={{ type: "spring", delay: 0.2 }}
                        className="relative"
                    >
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
                    </motion.div>

                    {/* Text */}
                    <div>
                        <h2 className="text-2xl font-bold text-white">Order Confirmed!</h2>
                        <p className="text-muted-foreground mt-2">
                            Thank you for your purchase. Your order is on its way!
                        </p>
                    </div>

                    {/* Button */}
                    <Button
                        onClick={onClose}
                        className="mt-2 bg-primary hover:bg-primary/90 hover:glow-primary"
                    >
                        Continue Shopping
                    </Button>
                </motion.div>
            </DialogContent>
        </Dialog>
    );
}
