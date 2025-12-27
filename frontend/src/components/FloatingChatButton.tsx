import { MessageSquare, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { motion, AnimatePresence } from "framer-motion";
import { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import { cn } from "@/lib/utils";

export const FloatingChatButton = () => {
  const [isHovered, setIsHovered] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated } = useAuth();
  
  // Don't show on chat page or login/register pages
  const shouldShow = location.pathname !== '/chat' && 
                     location.pathname !== '/login' && 
                     location.pathname !== '/register';

  if (!shouldShow) return null;

  const handleClick = () => {
    if (isAuthenticated) {
      navigate('/chat');
    } else {
      navigate('/login');
    }
  };

  return (
    <motion.div
      initial={{ scale: 0, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ delay: 1, type: "spring", stiffness: 260, damping: 20 }}
      className="fixed bottom-6 right-6 z-50"
      onHoverStart={() => setIsHovered(true)}
      onHoverEnd={() => setIsHovered(false)}
    >
      {/* Animated Ring */}
      <motion.div
        className="absolute inset-0 rounded-full bg-primary/20"
        animate={{
          scale: [1, 1.2, 1],
          opacity: [0.5, 0, 0.5],
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />
      
      {/* Tooltip */}
      <AnimatePresence>
        {isHovered && (
          <motion.div
            initial={{ opacity: 0, x: 10 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 10 }}
            className="absolute right-full mr-3 top-1/2 -translate-y-1/2 whitespace-nowrap"
          >
            <div className="bg-popover text-popover-foreground px-4 py-2 rounded-lg shadow-lg border border-border">
              <p className="text-sm font-medium">
                {isAuthenticated ? "Chat with AI Assistant" : "Login to Chat with AI"}
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                Get instant financial insights
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Button */}
      <Button
        size="lg"
        onClick={handleClick}
        className={cn(
          "h-16 w-16 rounded-full shadow-2xl transition-all duration-300",
          "bg-gradient-to-tr from-primary via-primary to-accent",
          "hover:shadow-primary/50 hover:scale-110",
          "relative overflow-hidden group"
        )}
      >
        {/* Shimmer Effect */}
        <motion.div
          className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent"
          animate={{
            x: ["-100%", "200%"],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            repeatDelay: 1,
          }}
        />
        
        <motion.div
          animate={isHovered ? { rotate: 0 } : { rotate: 0 }}
          transition={{ type: "spring", stiffness: 200 }}
        >
          <MessageSquare className="h-6 w-6 text-primary-foreground" />
        </motion.div>
      </Button>

      {/* Notification Badge (optional - shows new messages) */}
      <motion.div
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        className="absolute -top-1 -right-1 h-5 w-5 bg-red-500 rounded-full border-2 border-background flex items-center justify-center"
      >
        <span className="text-[10px] font-bold text-white">AI</span>
      </motion.div>
    </motion.div>
  );
};
