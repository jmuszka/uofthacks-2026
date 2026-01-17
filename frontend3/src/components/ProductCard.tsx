"use client";

import { Product } from "@/lib/mockData";
import { Checkbox } from "@/components/ui/checkbox";
import { motion } from "framer-motion";
import Image from "next/image";

interface ProductCardProps {
    product: Product;
    isSelected: boolean;
    onToggle: (product: Product) => void;
}

export function ProductCard({ product, isSelected, onToggle }: ProductCardProps) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            whileHover={{ scale: 1.02, y: -5 }}
            transition={{ duration: 0.3 }}
            onClick={() => onToggle(product)}
            className={`
        glass-card rounded-xl cursor-pointer overflow-hidden
        transition-all duration-300
        ${isSelected ? "ring-2 ring-primary glow-primary" : "hover:border-white/20"}
      `}
        >
            {/* Image */}
            <div className="relative aspect-square overflow-hidden">
                <Image
                    src={product.image}
                    alt={product.name}
                    fill
                    className="object-cover transition-transform duration-500 hover:scale-110"
                    unoptimized
                />
                {/* Gradient overlay */}
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />

                {/* Checkbox */}
                <div className="absolute top-3 right-3 z-10">
                    <div className="glass rounded-lg p-1">
                        <Checkbox
                            checked={isSelected}
                            onCheckedChange={() => onToggle(product)}
                            onClick={(e: React.MouseEvent) => e.stopPropagation()}
                            className="h-5 w-5 border-white/30 data-[state=checked]:bg-primary data-[state=checked]:border-primary"
                        />
                    </div>
                </div>

                {/* Price badge */}
                <div className="absolute bottom-3 right-3">
                    <span className="glass px-3 py-1 rounded-full text-lg font-bold text-primary">
                        ${product.price.toFixed(0)}
                    </span>
                </div>
            </div>

            {/* Content */}
            <div className="p-4 space-y-2">
                <h3 className="font-semibold text-lg text-white line-clamp-1">
                    {product.name}
                </h3>
                <p className="text-sm text-muted-foreground line-clamp-2">
                    {product.description}
                </p>

                {/* Store & Delivery */}
                <div className="flex items-center justify-between text-xs text-muted-foreground pt-2 border-t border-white/10">
                    <span className="flex items-center gap-1.5">
                        <span className="w-2 h-2 rounded-full bg-primary" />
                        {product.store}
                    </span>
                    <span className="flex items-center gap-1.5">
                        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        {product.deliveryTime}
                    </span>
                </div>
            </div>
        </motion.div>
    );
}
