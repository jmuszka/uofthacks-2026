"use client";

import { useState } from "react";
import { ChatInput } from "@/components/ChatInput";
import { ProductGrid } from "@/components/ProductGrid";
import { Cart } from "@/components/Cart";
import { Checkout, OrderSuccess } from "@/components/Checkout";
import { Button } from "@/components/ui/button";
import { Product, mockProducts } from "@/lib/mockData";
import { motion, AnimatePresence } from "framer-motion";
import { ShoppingCart, Sparkles } from "lucide-react";

export default function Home() {
  const [products, setProducts] = useState<Product[]>([]);
  const [selectedProducts, setSelectedProducts] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [isCartOpen, setIsCartOpen] = useState(false);
  const [isCheckoutOpen, setIsCheckoutOpen] = useState(false);
  const [isSuccessOpen, setIsSuccessOpen] = useState(false);

  const handleSearch = async (query: string) => {
    setIsLoading(true);
    setHasSearched(true);

    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 1200));

    // Mock: return random 4-6 products
    const shuffled = [...mockProducts].sort(() => 0.5 - Math.random());
    const count = Math.floor(Math.random() * 3) + 4;
    setProducts(shuffled.slice(0, count));
    setIsLoading(false);
  };

  const handleToggleProduct = (product: Product) => {
    setSelectedProducts((prev) => {
      const exists = prev.some((p) => p.id === product.id);
      if (exists) {
        return prev.filter((p) => p.id !== product.id);
      }
      return [...prev, product];
    });
  };

  const handleRemoveFromCart = (productId: string) => {
    setSelectedProducts((prev) => prev.filter((p) => p.id !== productId));
  };

  const handleCheckout = () => {
    setIsCartOpen(false);
    setIsCheckoutOpen(true);
  };

  const handleConfirmPurchase = () => {
    setIsCheckoutOpen(false);
    setIsSuccessOpen(true);
    setSelectedProducts([]);
    setProducts([]);
    setHasSearched(false);
  };

  return (
    <div className="min-h-screen bg-gradient-glow">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 z-50 glass border-b border-white/10">
        <div className="container mx-auto px-6 h-16 flex items-center justify-between">
          {/* Logo */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="flex items-center gap-2"
          >
            <div className="p-2 rounded-lg bg-primary/20">
              <Sparkles className="h-5 w-5 text-primary" />
            </div>
            <span className="text-xl font-bold text-white">Trovato</span>
          </motion.div>

          {/* Cart Button */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
          >
            <Button
              variant="outline"
              size="sm"
              className="relative glass border-white/10 hover:bg-white/5"
              onClick={() => setIsCartOpen(true)}
            >
              <ShoppingCart className="h-5 w-5" />
              <AnimatePresence>
                {selectedProducts.length > 0 && (
                  <motion.span
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    exit={{ scale: 0 }}
                    className="absolute -top-2 -right-2 h-5 w-5 rounded-full bg-primary text-primary-foreground text-xs flex items-center justify-center font-bold"
                  >
                    {selectedProducts.length}
                  </motion.span>
                )}
              </AnimatePresence>
            </Button>
          </motion.div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 pt-24 pb-32">
        {/* Hero / Welcome Section */}
        <AnimatePresence mode="wait">
          {!hasSearched && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0, y: -20 }}
              className="min-h-[60vh] flex flex-col items-center justify-center text-center"
            >
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="mb-12 space-y-4"
              >
                <h1 className="text-5xl md:text-7xl font-bold text-white leading-tight">
                  Hi, what would you
                  <br />
                  <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-accent">
                    like to shop for?
                  </span>
                </h1>
                <p className="text-xl text-muted-foreground">
                  Speak it. Cart it. Own it.
                </p>
              </motion.div>

              <ChatInput onSearch={handleSearch} isLoading={isLoading} />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Compact search after first search */}
        {hasSearched && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-8"
          >
            <ChatInput onSearch={handleSearch} isLoading={isLoading} />
          </motion.div>
        )}

        {/* Loading State */}
        <AnimatePresence>
          {isLoading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex flex-col items-center justify-center py-20 gap-6"
            >
              <div className="relative">
                <div className="h-16 w-16 rounded-full border-4 border-primary/30 border-t-primary animate-spin" />
                <div className="absolute inset-0 flex items-center justify-center">
                  <Sparkles className="h-6 w-6 text-primary animate-pulse" />
                </div>
              </div>
              <p className="text-muted-foreground text-lg">
                Finding the best products for you...
              </p>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Products Grid */}
        {!isLoading && products.length > 0 && (
          <ProductGrid
            products={products}
            selectedProducts={selectedProducts}
            onToggleProduct={handleToggleProduct}
          />
        )}

        {/* Empty state after search */}
        {!isLoading && hasSearched && products.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-20"
          >
            <p className="text-muted-foreground text-lg">
              No products found. Try a different search!
            </p>
          </motion.div>
        )}
      </main>

      {/* Floating Cart Button */}
      <AnimatePresence>
        {selectedProducts.length > 0 && !isCartOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.9 }}
            className="fixed bottom-6 left-1/2 -translate-x-1/2 z-40"
          >
            <Button
              size="lg"
              onClick={() => setIsCartOpen(true)}
              className="h-14 px-8 rounded-full bg-primary hover:bg-primary/90 glow-primary shadow-2xl gap-3"
            >
              <ShoppingCart className="h-5 w-5" />
              <span>View Cart ({selectedProducts.length})</span>
              <span className="font-bold">
                ${selectedProducts.reduce((sum, p) => sum + p.price, 0).toFixed(0)}
              </span>
            </Button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Cart Sidebar */}
      <Cart
        isOpen={isCartOpen}
        onClose={() => setIsCartOpen(false)}
        items={selectedProducts}
        onRemoveItem={handleRemoveFromCart}
        onCheckout={handleCheckout}
      />

      {/* Checkout Modal */}
      <Checkout
        isOpen={isCheckoutOpen}
        onClose={() => setIsCheckoutOpen(false)}
        items={selectedProducts}
        onConfirm={handleConfirmPurchase}
      />

      {/* Success Modal */}
      <OrderSuccess
        isOpen={isSuccessOpen}
        onClose={() => setIsSuccessOpen(false)}
      />
    </div>
  );
}
