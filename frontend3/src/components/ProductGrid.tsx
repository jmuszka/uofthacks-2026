"use client";

import { Product } from "@/lib/mockData";
import { ProductCard } from "./ProductCard";
import { motion } from "framer-motion";

interface ProductGridProps {
    products: Product[];
    selectedProducts: Product[];
    onToggleProduct: (product: Product) => void;
}

export function ProductGrid({ products, selectedProducts, onToggleProduct }: ProductGridProps) {
    if (products.length === 0) {
        return null;
    }

    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="w-full space-y-6"
        >
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="w-1 h-6 bg-primary rounded-full" />
                    <h2 className="text-xl font-semibold text-white">Results</h2>
                </div>
                <span className="text-sm text-muted-foreground glass px-3 py-1 rounded-full">
                    {products.length} products found
                </span>
            </div>

            {/* Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {products.map((product, index) => (
                    <motion.div
                        key={product.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.1 }}
                    >
                        <ProductCard
                            product={product}
                            isSelected={selectedProducts.some((p) => p.id === product.id)}
                            onToggle={onToggleProduct}
                        />
                    </motion.div>
                ))}
            </div>
        </motion.div>
    );
}
