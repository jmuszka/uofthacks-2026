"use client";

import { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import { motion, AnimatePresence } from "framer-motion";
import {
    Camera,
    Upload,
    User,
    ArrowRight,
    ArrowLeft,
    Sparkles,
    MapPin,
    Shirt,
    Leaf,
    DollarSign,
    X
} from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { supabase } from "@/lib/supabase";
import { useRouter } from "next/navigation";

type Step = "welcome" | "photo" | "sizes" | "style" | "values" | "budget" | "complete";

interface UserProfile {
    name: string;
    email: string;
    password?: string;
    photo: string | null;
    sizes: {
        clothing: string;
        waist: string;
        shoe: string;
        fit: string;
    };
    style: string[];
    customStyle: string;
    values: string[];
    customValue: string;
    budget: number;
    zipCode: string;
}

const styleOptions = [
    { id: "streetwear", label: "Streetwear", emoji: "🔥" },
    { id: "minimalist", label: "Minimalist", emoji: "⚪" },
];

const valueOptions = [
    { id: "local", label: "Made Locally" },
    { id: "eco-friendly", label: "Eco-Friendly" },
];

export default function LoginPage() {
    const [step, setStep] = useState<Step>("welcome");
    const [profile, setProfile] = useState<UserProfile>({
        name: "",
        email: "",
        photo: null,
        sizes: { clothing: "", waist: "", shoe: "", fit: "" },
        style: [],
        customStyle: "",
        values: [],
        customValue: "",
        budget: 50,
        zipCode: "",
    });
    const [authMode, setAuthMode] = useState<"signup" | "login">("signup");
    const [authError, setAuthError] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const router = useRouter();

    const handleAuth = async () => {
        if (!profile.email || !profile.password) {
            setAuthError("Email and password are required");
            return;
        }

        setIsLoading(true);
        setAuthError(null);

        try {
            if (authMode === "signup") {
                const { error } = await supabase.auth.signUp({
                    email: profile.email,
                    password: profile.password,
                    options: {
                        data: {
                            full_name: profile.name,
                        },
                    },
                });
                if (error) throw error;
                // Continue with profile creation flow
                nextStep();
            } else {
                const { error } = await supabase.auth.signInWithPassword({
                    email: profile.email,
                    password: profile.password,
                });
                if (error) throw error;
                router.push("/");
            }
        } catch (error: any) {
            setAuthError(error.message);
        } finally {
            setIsLoading(false);
        }
    };

    const handlePhotoUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            const reader = new FileReader();
            reader.onloadend = () => {
                setProfile((prev) => ({ ...prev, photo: reader.result as string }));
            };
            reader.readAsDataURL(file);
        }
    };

    const handleStyleToggle = (styleId: string) => {
        setProfile((prev) => ({
            ...prev,
            style: prev.style.includes(styleId)
                ? prev.style.filter((s) => s !== styleId)
                : [...prev.style, styleId],
        }));
    };

    const handleValueToggle = (valueId: string) => {
        setProfile((prev) => ({
            ...prev,
            values: prev.values.includes(valueId)
                ? prev.values.filter((v) => v !== valueId)
                : [...prev.values, valueId],
        }));
    };

    const nextStep = () => {
        const steps: Step[] = ["welcome", "photo", "sizes", "style", "values", "budget", "complete"];
        const currentIndex = steps.indexOf(step);
        if (currentIndex < steps.length - 1) {
            setStep(steps[currentIndex + 1]);
        }
    };

    const prevStep = () => {
        const steps: Step[] = ["welcome", "photo", "sizes", "style", "values", "budget", "complete"];
        const currentIndex = steps.indexOf(step);
        if (currentIndex > 0) {
            setStep(steps[currentIndex - 1]);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-glow flex items-center justify-center p-6">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="w-full max-w-md glass-card rounded-2xl p-8 space-y-6"
            >
                {/* Header */}
                <div className="text-center space-y-2">
                    <Link href="/" className="inline-flex items-center gap-2 hover:opacity-80 transition-opacity">
                        <span className="text-2xl font-bold text-white">Trovato</span>
                    </Link>
                </div>

                <AnimatePresence mode="wait">
                    {/* Welcome Step */}
                    {step === "welcome" && (
                        <motion.div
                            key="welcome"
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                            className="space-y-6"
                        >
                            <div className="text-center space-y-2">
                                <h2 className="text-xl font-semibold text-white">
                                    {authMode === "signup" ? "Create Your Profile" : "Welcome Back"}
                                </h2>
                                <p className="text-sm text-muted-foreground">
                                    {authMode === "signup"
                                        ? "Help us find products tailored just for you"
                                        : "Sign in to access your profile"}
                                </p>
                            </div>

                            <div className="space-y-4">
                                {authMode === "signup" && (
                                    <div>
                                        <label className="text-sm text-muted-foreground mb-2 block">Name</label>
                                        <Input
                                            placeholder="Your name"
                                            value={profile.name}
                                            onChange={(e) => setProfile((prev) => ({ ...prev, name: e.target.value }))}
                                            className="glass-input h-12"
                                        />
                                    </div>
                                )}
                                <div>
                                    <label className="text-sm text-muted-foreground mb-2 block">Email</label>
                                    <Input
                                        type="email"
                                        placeholder="your@email.com"
                                        value={profile.email}
                                        onChange={(e) => setProfile((prev) => ({ ...prev, email: e.target.value }))}
                                        className="glass-input h-12"
                                    />
                                </div>
                                <div>
                                    <label className="text-sm text-muted-foreground mb-2 block">Password</label>
                                    <Input
                                        type="password"
                                        placeholder="••••••••"
                                        value={profile.password || ""}
                                        onChange={(e) => setProfile((prev) => ({ ...prev, password: e.target.value }))}
                                        className="glass-input h-12"
                                    />
                                </div>
                            </div>

                            {authError && (
                                <div className="text-red-500 text-sm text-center bg-red-500/10 p-2 rounded">
                                    {authError}
                                </div>
                            )}

                            <div className="space-y-3">
                                <Button
                                    onClick={handleAuth}
                                    disabled={!profile.email || !profile.password || (authMode === "signup" && !profile.name) || isLoading}
                                    className="w-full h-12 bg-primary hover:bg-primary/90 gap-2"
                                >
                                    {isLoading ? "Processing..." : (authMode === "signup" ? "Continue" : "Log In")}
                                    {!isLoading && <ArrowRight className="h-4 w-4" />}
                                </Button>

                                <div className="text-center">
                                    <button
                                        onClick={() => {
                                            setAuthMode(authMode === "signup" ? "login" : "signup");
                                            setAuthError(null);
                                        }}
                                        className="text-sm text-muted-foreground hover:text-white transition-colors"
                                    >
                                        {authMode === "signup"
                                            ? "Already have an account? Log in"
                                            : "Don't have an account? Sign up"}
                                    </button>
                                </div>
                            </div>
                        </motion.div>
                    )}

                    {/* Photo Step */}
                    {step === "photo" && (
                        <motion.div
                            key="photo"
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                            className="space-y-6"
                        >
                            <div className="text-center space-y-2">
                                <Camera className="h-8 w-8 text-primary mx-auto" />
                                <h2 className="text-xl font-semibold text-white">Upload Your Look</h2>
                                <p className="text-sm text-muted-foreground">
                                    We'll use AI to understand your style
                                </p>
                            </div>

                            <div className="flex flex-col items-center gap-4">
                                {profile.photo ? (
                                    <div className="relative">
                                        <Image
                                            src={profile.photo}
                                            alt="Your photo"
                                            width={150}
                                            height={150}
                                            className="rounded-full object-cover h-36 w-36"
                                        />
                                        <Button
                                            size="icon"
                                            variant="destructive"
                                            className="absolute -top-2 -right-2 h-8 w-8 rounded-full"
                                            onClick={() => setProfile((prev) => ({ ...prev, photo: null }))}
                                        >
                                            <X className="h-4 w-4" />
                                        </Button>
                                    </div>
                                ) : (
                                    <div
                                        onClick={() => fileInputRef.current?.click()}
                                        className="h-36 w-36 rounded-full border-2 border-dashed border-white/20 flex flex-col items-center justify-center cursor-pointer hover:border-primary/50 transition-colors"
                                    >
                                        <User className="h-12 w-12 text-muted-foreground" />
                                        <span className="text-xs text-muted-foreground mt-2">Click to upload</span>
                                    </div>
                                )}
                                <input
                                    ref={fileInputRef}
                                    type="file"
                                    accept="image/*"
                                    capture="user"
                                    onChange={handlePhotoUpload}
                                    className="hidden"
                                />
                                <div className="flex gap-2">
                                    <Button
                                        variant="outline"
                                        size="sm"
                                        onClick={() => fileInputRef.current?.click()}
                                        className="glass border-white/10 gap-2"
                                    >
                                        <Upload className="h-4 w-4" /> From Library
                                    </Button>
                                    <Button
                                        variant="outline"
                                        size="sm"
                                        onClick={() => {
                                            if (fileInputRef.current) {
                                                fileInputRef.current.setAttribute("capture", "user");
                                                fileInputRef.current.click();
                                            }
                                        }}
                                        className="glass border-white/10 gap-2"
                                    >
                                        <Camera className="h-4 w-4" /> Take Photo
                                    </Button>
                                </div>
                            </div>

                            <div className="flex gap-3">
                                <Button variant="outline" onClick={prevStep} className="flex-1 glass border-white/10">
                                    <ArrowLeft className="h-4 w-4 mr-2" /> Back
                                </Button>
                                <Button onClick={nextStep} className="flex-1 bg-primary hover:bg-primary/90">
                                    {profile.photo ? "Continue" : "Skip"} <ArrowRight className="h-4 w-4 ml-2" />
                                </Button>
                            </div>
                        </motion.div>
                    )}

                    {/* Sizes Step */}
                    {step === "sizes" && (
                        <motion.div
                            key="sizes"
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                            className="space-y-6"
                        >
                            <div className="text-center space-y-2">
                                <Shirt className="h-8 w-8 text-primary mx-auto" />
                                <h2 className="text-xl font-semibold text-white">Your Fit Profile</h2>
                                <p className="text-sm text-muted-foreground">
                                    Help us find the perfect fit
                                </p>
                            </div>

                            <div className="space-y-4">
                                <div className="grid grid-cols-2 gap-3">
                                    <div>
                                        <label className="text-xs text-muted-foreground mb-1 block">Clothing Size</label>
                                        <select
                                            value={profile.sizes.clothing}
                                            onChange={(e) => setProfile((prev) => ({
                                                ...prev,
                                                sizes: { ...prev.sizes, clothing: e.target.value }
                                            }))}
                                            className="w-full h-10 px-3 rounded-lg glass-input text-white text-sm bg-[#1a1a2e] border border-white/10 appearance-none cursor-pointer"
                                            style={{ backgroundColor: '#1a1a2e' }}
                                        >
                                            <option value="" className="bg-[#1a1a2e] text-white">Select</option>
                                            <option value="XS" className="bg-[#1a1a2e] text-white">XS</option>
                                            <option value="S" className="bg-[#1a1a2e] text-white">S</option>
                                            <option value="M" className="bg-[#1a1a2e] text-white">M</option>
                                            <option value="L" className="bg-[#1a1a2e] text-white">L</option>
                                            <option value="XL" className="bg-[#1a1a2e] text-white">XL</option>
                                            <option value="XXL" className="bg-[#1a1a2e] text-white">XXL</option>
                                        </select>
                                    </div>
                                    <div>
                                        <label className="text-xs text-muted-foreground mb-1 block">Shoe Size</label>
                                        <Input
                                            placeholder="e.g., 10.5"
                                            value={profile.sizes.shoe}
                                            onChange={(e) => setProfile((prev) => ({
                                                ...prev,
                                                sizes: { ...prev.sizes, shoe: e.target.value }
                                            }))}
                                            className="glass-input h-10"
                                        />
                                    </div>
                                </div>

                                <div>
                                    <label className="text-xs text-muted-foreground mb-2 block">Fit Preference</label>
                                    <div className="grid grid-cols-3 gap-2">
                                        {["Slim", "Regular", "Oversized"].map((fit) => (
                                            <Button
                                                key={fit}
                                                variant={profile.sizes.fit === fit ? "default" : "outline"}
                                                size="sm"
                                                onClick={() => setProfile((prev) => ({
                                                    ...prev,
                                                    sizes: { ...prev.sizes, fit }
                                                }))}
                                                className={profile.sizes.fit === fit ? "bg-primary" : "glass border-white/10"}
                                            >
                                                {fit}
                                            </Button>
                                        ))}
                                    </div>
                                </div>
                            </div>

                            <div className="flex gap-3">
                                <Button variant="outline" onClick={prevStep} className="flex-1 glass border-white/10">
                                    <ArrowLeft className="h-4 w-4 mr-2" /> Back
                                </Button>
                                <Button onClick={nextStep} className="flex-1 bg-primary hover:bg-primary/90">
                                    Continue <ArrowRight className="h-4 w-4 ml-2" />
                                </Button>
                            </div>
                        </motion.div>
                    )}

                    {/* Style Step */}
                    {step === "style" && (
                        <motion.div
                            key="style"
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                            className="space-y-6"
                        >
                            <div className="text-center space-y-2">
                                <Sparkles className="h-8 w-8 text-primary mx-auto" />
                                <h2 className="text-xl font-semibold text-white">Your Vibe</h2>
                                <p className="text-sm text-muted-foreground">
                                    Select the styles that match you
                                </p>
                            </div>

                            <div className="grid grid-cols-2 gap-3">
                                {styleOptions.map((style) => (
                                    <Button
                                        key={style.id}
                                        variant={profile.style.includes(style.id) ? "default" : "outline"}
                                        onClick={() => handleStyleToggle(style.id)}
                                        className={`h-16 flex-col gap-1 ${profile.style.includes(style.id) ? "bg-primary glow-primary" : "glass border-white/10"
                                            }`}
                                    >
                                        <span className="text-xl">{style.emoji}</span>
                                        <span className="text-xs">{style.label}</span>
                                    </Button>
                                ))}
                            </div>

                            {/* Custom style input */}
                            <div>
                                <label className="text-xs text-muted-foreground mb-2 block">Other style (optional)</label>
                                <Input
                                    placeholder="Describe your style..."
                                    value={profile.customStyle}
                                    onChange={(e) => setProfile((prev) => ({ ...prev, customStyle: e.target.value.slice(0, 20) }))}
                                    maxLength={20}
                                    className="glass-input h-10"
                                />
                                <span className="text-xs text-muted-foreground">{profile.customStyle.length}/20</span>
                            </div>

                            <div className="flex gap-3">
                                <Button variant="outline" onClick={prevStep} className="flex-1 glass border-white/10">
                                    <ArrowLeft className="h-4 w-4 mr-2" /> Back
                                </Button>
                                <Button onClick={nextStep} className="flex-1 bg-primary hover:bg-primary/90">
                                    Continue <ArrowRight className="h-4 w-4 ml-2" />
                                </Button>
                            </div>
                        </motion.div>
                    )}

                    {/* Values Step */}
                    {step === "values" && (
                        <motion.div
                            key="values"
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                            className="space-y-6"
                        >
                            <div className="text-center space-y-2">
                                <Leaf className="h-8 w-8 text-primary mx-auto" />
                                <h2 className="text-xl font-semibold text-white">Your Values</h2>
                                <p className="text-sm text-muted-foreground">
                                    What matters to you when shopping?
                                </p>
                            </div>

                            <div className="space-y-3">
                                {valueOptions.map((value) => (
                                    <div
                                        key={value.id}
                                        onClick={() => handleValueToggle(value.id)}
                                        className={`flex items-center gap-3 p-3 rounded-lg cursor-pointer transition-all ${profile.values.includes(value.id)
                                            ? "glass ring-2 ring-primary"
                                            : "glass border-white/10 hover:bg-white/5"
                                            }`}
                                    >
                                        <Checkbox checked={profile.values.includes(value.id)} />
                                        <span className="text-sm text-white">{value.label}</span>
                                    </div>
                                ))}
                            </div>

                            {/* Custom value input */}
                            <div>
                                <label className="text-xs text-muted-foreground mb-2 block">Other value (optional)</label>
                                <Input
                                    placeholder="What else matters to you..."
                                    value={profile.customValue}
                                    onChange={(e) => setProfile((prev) => ({ ...prev, customValue: e.target.value.slice(0, 20) }))}
                                    maxLength={20}
                                    className="glass-input h-10"
                                />
                                <span className="text-xs text-muted-foreground">{profile.customValue.length}/20</span>
                            </div>

                            <div className="flex gap-3">
                                <Button variant="outline" onClick={prevStep} className="flex-1 glass border-white/10">
                                    <ArrowLeft className="h-4 w-4 mr-2" /> Back
                                </Button>
                                <Button onClick={nextStep} className="flex-1 bg-primary hover:bg-primary/90">
                                    Continue <ArrowRight className="h-4 w-4 ml-2" />
                                </Button>
                            </div>
                        </motion.div>
                    )}

                    {/* Budget Step */}
                    {step === "budget" && (
                        <motion.div
                            key="budget"
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                            className="space-y-6"
                        >
                            <div className="text-center space-y-2">
                                <DollarSign className="h-8 w-8 text-primary mx-auto" />
                                <h2 className="text-xl font-semibold text-white">Budget & Location</h2>
                                <p className="text-sm text-muted-foreground">
                                    Almost done! Tell us your preferences
                                </p>
                            </div>

                            <div className="space-y-4">
                                <div className="space-y-4">
                                    <div className="flex justify-between text-sm text-muted-foreground">
                                        <span>💵 Budget</span>
                                        <span>💎 Luxury</span>
                                    </div>
                                    <input
                                        type="range"
                                        min="0"
                                        max="100"
                                        value={profile.budget}
                                        onChange={(e) => setProfile((prev) => ({ ...prev, budget: parseInt(e.target.value) }))}
                                        className="w-full h-2 bg-white/10 rounded-lg appearance-none cursor-pointer accent-primary"
                                        style={{
                                            background: `linear-gradient(to right, hsl(var(--primary)) 0%, hsl(var(--primary)) ${profile.budget}%, rgba(255,255,255,0.1) ${profile.budget}%, rgba(255,255,255,0.1) 100%)`
                                        }}
                                    />
                                    <div className="text-center">
                                        <span className="text-sm text-white font-medium">
                                            {profile.budget <= 33 ? "Budget-Friendly" : profile.budget <= 66 ? "Mid-Range" : "Luxury"}
                                        </span>
                                    </div>
                                </div>

                                <div>
                                    <label className="text-xs text-muted-foreground mb-2 block flex items-center gap-1">
                                        <MapPin className="h-3 w-3" /> Zip Code (for shipping estimates)
                                    </label>
                                    <Input
                                        placeholder="Enter your zip code"
                                        value={profile.zipCode}
                                        onChange={(e) => setProfile((prev) => ({ ...prev, zipCode: e.target.value }))}
                                        className="glass-input h-12"
                                    />
                                </div>
                            </div>

                            <div className="flex gap-3">
                                <Button variant="outline" onClick={prevStep} className="flex-1 glass border-white/10">
                                    <ArrowLeft className="h-4 w-4 mr-2" /> Back
                                </Button>
                                <Button onClick={nextStep} className="flex-1 bg-primary hover:bg-primary/90">
                                    Complete <ArrowRight className="h-4 w-4 ml-2" />
                                </Button>
                            </div>
                        </motion.div>
                    )}

                    {/* Complete Step */}
                    {step === "complete" && (
                        <motion.div
                            key="complete"
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            className="space-y-6 text-center"
                        >
                            <motion.div
                                initial={{ scale: 0 }}
                                animate={{ scale: 1 }}
                                transition={{ type: "spring", delay: 0.2 }}
                                className="h-20 w-20 rounded-full bg-primary/20 flex items-center justify-center mx-auto glow-primary"
                            >
                                <Sparkles className="h-10 w-10 text-primary" />
                            </motion.div>

                            <div>
                                <h2 className="text-2xl font-bold text-white">You're All Set!</h2>
                                <p className="text-muted-foreground mt-2">
                                    Welcome to Trovato, {profile.name}!
                                </p>
                            </div>

                            <Link href="/">
                                <Button className="w-full h-12 bg-primary hover:bg-primary/90 gap-2">
                                    Start Shopping <ArrowRight className="h-4 w-4" />
                                </Button>
                            </Link>
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Progress dots */}
                {step !== "complete" && (
                    <div className="flex justify-center gap-2 pt-4">
                        {["welcome", "photo", "sizes", "style", "values", "budget"].map((s) => (
                            <div
                                key={s}
                                className={`h-2 w-2 rounded-full transition-all ${s === step ? "bg-primary w-6" : "bg-white/20"
                                    }`}
                            />
                        ))}
                    </div>
                )}
            </motion.div>
        </div>
    );
}
