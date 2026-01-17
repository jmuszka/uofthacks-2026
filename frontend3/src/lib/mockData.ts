// Mock product data for testing the UI without backend
export interface Product {
    id: string;
    name: string;
    price: number;
    image: string;
    store: string;
    deliveryTime: string;
    description: string;
}

export const mockProducts: Product[] = [
    {
        id: "1",
        name: "Nike Air Max 270",
        price: 150.00,
        image: "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&h=400&fit=crop",
        store: "Nike Store",
        deliveryTime: "2-3 days",
        description: "Comfortable running shoes with Air Max cushioning"
    },
    {
        id: "2",
        name: "Adidas Ultraboost 22",
        price: 180.00,
        image: "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=400&h=400&fit=crop",
        store: "Adidas Official",
        deliveryTime: "3-5 days",
        description: "Premium running shoes with Boost technology"
    },
    {
        id: "3",
        name: "New Balance 990v5",
        price: 175.00,
        image: "https://images.unsplash.com/photo-1539185441755-769473a23570?w=400&h=400&fit=crop",
        store: "New Balance",
        deliveryTime: "2-4 days",
        description: "Classic design meets modern comfort"
    },
    {
        id: "4",
        name: "Puma RS-X",
        price: 110.00,
        image: "https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=400&h=400&fit=crop",
        store: "Puma Store",
        deliveryTime: "4-6 days",
        description: "Retro-inspired sneakers with bold design"
    },
    {
        id: "5",
        name: "Converse Chuck Taylor",
        price: 65.00,
        image: "https://images.unsplash.com/photo-1607522370275-f14206abe5d3?w=400&h=400&fit=crop",
        store: "Converse",
        deliveryTime: "2-3 days",
        description: "Timeless classic canvas sneakers"
    },
    {
        id: "6",
        name: "Vans Old Skool",
        price: 70.00,
        image: "https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?w=400&h=400&fit=crop",
        store: "Vans",
        deliveryTime: "3-4 days",
        description: "Iconic skate shoes with signature side stripe"
    },
    {
        id: "7",
        name: "Reebok Classic Leather",
        price: 85.00,
        image: "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=400&h=400&fit=crop",
        store: "Reebok",
        deliveryTime: "3-5 days",
        description: "Heritage leather sneakers with cushioned comfort"
    },
    {
        id: "8",
        name: "ASICS Gel-Kayano 29",
        price: 160.00,
        image: "https://images.unsplash.com/photo-1560769629-975ec94e6a86?w=400&h=400&fit=crop",
        store: "ASICS",
        deliveryTime: "2-4 days",
        description: "Stability running shoes with gel cushioning"
    }
];
