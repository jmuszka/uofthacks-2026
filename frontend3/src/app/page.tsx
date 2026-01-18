"use client";

import { useState, useMemo, useEffect } from "react";
import { ChatInput } from "@/components/ChatInput";
import { ProductGrid } from "@/components/ProductGrid";
import { Cart } from "@/components/Cart";
import { Checkout, OrderSuccess } from "@/components/Checkout";
import { FloatingChat } from "@/components/FloatingChat";
import { Recommendations } from "@/components/Recommendations";
import { SortingControls, SortOption } from "@/components/SortingControls";
import { Button } from "@/components/ui/button";
import { Product, mockProducts } from "@/lib/mockData";
import { motion, AnimatePresence } from "framer-motion";
import { ShoppingCart, Home, User, Settings, HelpCircle } from "lucide-react";
import Image from "next/image";

export default function HomePage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [recommendations, setRecommendations] = useState<Product[]>([]);
  const [selectedProducts, setSelectedProducts] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [currentQuery, setCurrentQuery] = useState("");
  const [sortBy, setSortBy] = useState<SortOption>("relevance");
  const [isCartOpen, setIsCartOpen] = useState(false);
  const [isCheckoutOpen, setIsCheckoutOpen] = useState(false);
  const [isSuccessOpen, setIsSuccessOpen] = useState(false);

  const handleGoHome = () => {
    setProducts([]);
    setRecommendations([]);
    setHasSearched(false);
    setCurrentQuery("");
    setSortBy("relevance");
  };

  useEffect(() => {
    setIsLoading(false)
  }, [products]) 

  const handleSearch = async (query: string) => {
    console.log("bruh")

    setIsLoading(true);
    setHasSearched(true);
    setCurrentQuery(query);

    // Retrieve products from backend
    fetch("http://localhost:8080/search", {
      method: "POST",
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        'query': query
      })
    })
    .then(res => res.json())
    .then(data => JSON.parse(data.items).map((product): Product => {
      return {
        id: crypto.randomUUID(),
        name: product["name"],
        price: Number(product["price"]),
        image: "url",
        store: product["link"],
        deliveryTime: "unknown",
        description: product["description"],
      }
    }))
    .then(data => {setProducts(data)})

    // Mock: return random 4-6 products
    // const shuffled = [...mockProducts].sort(() => 0.5 - Math.random());
    // const count = Math.floor(Math.random() * 3) + 4;
    // setProducts(shuffled.slice(0, count));

    // Mock recommendations (remaining products)
    // setRecommendations(shuffled.slice(count, count + 4));
    // setIsLoading(false);
  };

  // Sort products based on current sort option
  const sortedProducts = useMemo(() => {
    const sorted = [...products];
    switch (sortBy) {
      case "price-low":
        return sorted.sort((a, b) => a.price - b.price);
      case "price-high":
        return sorted.sort((a, b) => b.price - a.price);
      case "delivery":
        return sorted.sort((a, b) => {
          const getMinDays = (time: string) => parseInt(time.split("-")[0]) || 0;
          return getMinDays(a.deliveryTime) - getMinDays(b.deliveryTime);
        });
      case "rating":
      case "relevance":
      default:
        return sorted;
    }
  }, [products, sortBy]);

  const handleToggleProduct = (product: Product) => {
    setSelectedProducts((prev) => {
      const exists = prev.some((p) => p.id === product.id);
      if (exists) {
        return prev.filter((p) => p.id !== product.id);
      }
      return [...prev, product];
    });
  };

  const handleAddRecommendation = (product: Product) => {
    if (!selectedProducts.some((p) => p.id === product.id)) {
      setSelectedProducts((prev) => [...prev, product]);
    }
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
    setRecommendations([]);
    setHasSearched(false);
    setCurrentQuery("");
  };

  const handleChatMessage = (message: string) => {
    // This will be connected to the Gemini API
    console.log("Chat message:", message);
    handleSearch(message);
  };

  return (
    <div className="min-h-screen bg-gradient-glow">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 z-50 glass border-b border-white/10">
        <div className="container mx-auto px-6 h-16 flex items-center justify-between">
          {/* Logo + Navigation grouped together */}
          <div className="flex items-center gap-6">
            {/* Logo - Clickable to go home */}
            <motion.button
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              onClick={handleGoHome}
              className="flex items-center gap-2 hover:opacity-80 transition-all duration-200 hover:scale-105"
            >
              <Image
                src="/logo1.png"
                alt="Trovato"
                width={40}
                height={40}
                className="rounded-lg"
              />
              <span className="text-xl font-bold text-white">Trovato</span>
            </motion.button>

            {/* Navigation - next to logo */}
            <motion.nav
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="hidden md:flex items-center gap-1"
            >
              <Button
                variant="ghost"
                size="sm"
                onClick={handleGoHome}
                className="text-muted-foreground hover:text-white hover:bg-white/5 gap-2 transition-all duration-200"
              >
                <Home className="h-4 w-4" />
                Home
              </Button>
              <Button
                variant="ghost"
                size="sm"
                className="text-muted-foreground hover:text-white hover:bg-white/5 gap-2 transition-all duration-200"
              >
                <HelpCircle className="h-4 w-4" />
                How it Works
              </Button>
              <Button
                variant="ghost"
                size="sm"
                className="text-muted-foreground hover:text-white hover:bg-white/5 gap-2 transition-all duration-200"
              >
                <Settings className="h-4 w-4" />
                Settings
              </Button>
              <a href="/login">
                <Button
                  variant="ghost"
                  size="sm"
                  className="text-muted-foreground hover:text-white hover:bg-white/5 gap-2 transition-all duration-200"
                >
                  <User className="h-4 w-4" />
                  Login
                </Button>
              </a>
            </motion.nav>
          </div>

          {/* Cart Button */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
          >
            <Button
              variant="outline"
              size="sm"
              className="relative glass border-white/10 hover:bg-white/5 transition-all duration-200"
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

        {/* Results Header with Sorting */}
        {hasSearched && !isLoading && products.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6 space-y-4"
          >
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <div className="flex items-center gap-3">
                <div className="w-1 h-6 bg-primary rounded-full" />
                <h2 className="text-xl font-semibold text-white">Results</h2>
                <span className="text-sm text-muted-foreground glass px-3 py-1 rounded-full">
                  {products.length} products
                </span>
              </div>
              <SortingControls currentSort={sortBy} onSortChange={setSortBy} />
            </div>
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
                  <Image
                    src="/logo.png"
                    alt="Loading"
                    width={32}
                    height={32}
                    className="animate-pulse rounded-md"
                  />
                </div>
              </div>
              <p className="text-muted-foreground text-lg">
                Finding the best products for you...
              </p>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Products Grid */}
        {!isLoading && sortedProducts.length > 0 && (
          <>
            <ProductGrid
              products={sortedProducts}
              selectedProducts={selectedProducts}
              onToggleProduct={handleToggleProduct}
            />

            {/* Recommendations Section */}
            <Recommendations
              products={recommendations}
              selectedProducts={selectedProducts}
              onToggleProduct={handleToggleProduct}
            />
          </>
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

      {/* Floating Chat - only show after first search */}
      {hasSearched && !isLoading && (
        <FloatingChat
          onSendMessage={handleChatMessage}
          isLoading={isLoading}
          initialQuery={currentQuery}
        />
      )}

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
