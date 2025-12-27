import { useState, useEffect } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Wallet, 
  Target, 
  Brain, 
  Check,
  ArrowRight,
  Sparkles,
  LucideIcon
} from "lucide-react";
import { cn } from "@/lib/utils";

interface OnboardingStep {
  id: number;
  icon: LucideIcon;
  title: string;
  description: string;
  action: string;
}

const steps: OnboardingStep[] = [
  {
    id: 1,
    icon: Wallet,
    title: "Connect Your Finances",
    description: "Add your income, expenses, investments, and loans to get a complete financial picture.",
    action: "Add Income"
  },
  {
    id: 2,
    icon: Target,
    title: "Set Your Goals",
    description: "Define your financial goals and let our AI help you create a roadmap to achieve them.",
    action: "Set Goals"
  },
  {
    id: 3,
    icon: Brain,
    title: "Get AI Insights",
    description: "Chat with our AI assistant anytime for personalized financial advice and insights.",
    action: "Try AI Chat"
  }
];

interface OnboardingModalProps {
  onComplete: (step?: number) => void;
}

export const OnboardingModal = ({ onComplete }: OnboardingModalProps) => {
  const [open, setOpen] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);

  useEffect(() => {
    // Check if user has seen onboarding
    const hasSeenOnboarding = localStorage.getItem('hasSeenOnboarding');
    if (!hasSeenOnboarding) {
      // Show modal after a short delay
      setTimeout(() => setOpen(true), 1000);
    }
  }, []);

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      handleComplete();
    }
  };

  const handleSkip = () => {
    handleComplete();
  };

  const handleComplete = () => {
    localStorage.setItem('hasSeenOnboarding', 'true');
    setOpen(false);
    onComplete();
  };

  const handleAction = () => {
    localStorage.setItem('hasSeenOnboarding', 'true');
    setOpen(false);
    onComplete(currentStep);
  };

  const step = steps[currentStep];

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogContent className="sm:max-w-[500px] overflow-hidden p-0">
        <div className="relative">
          {/* Background Gradient */}
          <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-background to-accent/10 -z-10" />
          
          <div className="p-6">
            {/* Header */}
            <DialogHeader className="space-y-4">
              <div className="flex items-center justify-between">
                <DialogTitle className="text-2xl font-bold flex items-center gap-2">
                  <Sparkles className="h-6 w-6 text-primary" />
                  Welcome to Clarifi AI
                </DialogTitle>
                <Button variant="ghost" size="sm" onClick={handleSkip}>
                  Skip
                </Button>
              </div>
              
              {/* Progress Indicators */}
              <div className="flex gap-2">
                {steps.map((s, i) => (
                  <div
                    key={s.id}
                    className={cn(
                      "h-1.5 flex-1 rounded-full transition-all duration-300",
                      i <= currentStep ? "bg-primary" : "bg-muted"
                    )}
                  />
                ))}
              </div>
            </DialogHeader>

            {/* Content */}
            <AnimatePresence mode="wait">
              <motion.div
                key={currentStep}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.3 }}
                className="mt-8 space-y-6"
              >
                {/* Icon */}
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ 
                    type: "spring", 
                    stiffness: 200, 
                    damping: 15,
                    delay: 0.1 
                  }}
                  className="flex justify-center"
                >
                  <div className="relative">
                    <div className="absolute inset-0 bg-primary/20 blur-xl rounded-full" />
                    <div className="relative bg-gradient-to-br from-primary to-accent p-6 rounded-2xl">
                      <step.icon className="h-12 w-12 text-primary-foreground" />
                    </div>
                  </div>
                </motion.div>

                {/* Text Content */}
                <div className="text-center space-y-3">
                  <DialogDescription asChild>
                    <div>
                      <h3 className="text-xl font-semibold text-foreground mb-2">
                        {step.title}
                      </h3>
                      <p className="text-muted-foreground">
                        {step.description}
                      </p>
                    </div>
                  </DialogDescription>
                </div>

                {/* Actions */}
                <div className="flex gap-3 pt-4">
                  {currentStep < steps.length - 1 ? (
                    <>
                      <Button
                        variant="outline"
                        className="flex-1"
                        onClick={handleAction}
                      >
                        {step.action}
                      </Button>
                      <Button
                        className="flex-1 gap-2"
                        onClick={handleNext}
                      >
                        Next
                        <ArrowRight className="h-4 w-4" />
                      </Button>
                    </>
                  ) : (
                    <Button
                      className="w-full gap-2"
                      onClick={handleComplete}
                    >
                      <Check className="h-4 w-4" />
                      Get Started
                    </Button>
                  )}
                </div>
              </motion.div>
            </AnimatePresence>

            {/* Step Counter */}
            <div className="text-center mt-6 text-sm text-muted-foreground">
              Step {currentStep + 1} of {steps.length}
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};
