import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { 
  DollarSign, 
  TrendingUp, 
  Wallet, 
  ShoppingCart,
  Home,
  Car,
  Utensils,
  ShoppingBag,
  Heart,
  Plane,
  Lightbulb,
  Users
} from "lucide-react";

interface AnimatedIconProps {
  type: 'income' | 'expense' | 'investment' | 'savings' | 'food' | 'housing' | 'transport' | 'shopping' | 'health' | 'travel' | 'utilities' | 'family';
  size?: number;
  className?: string;
}

const iconMap = {
  income: DollarSign,
  expense: Wallet,
  investment: TrendingUp,
  savings: Wallet,
  food: Utensils,
  housing: Home,
  transport: Car,
  shopping: ShoppingCart,
  health: Heart,
  travel: Plane,
  utilities: Lightbulb,
  family: Users,
};

const colorMap = {
  income: "text-green-500",
  expense: "text-red-500",
  investment: "text-blue-500",
  savings: "text-purple-500",
  food: "text-orange-500",
  housing: "text-indigo-500",
  transport: "text-cyan-500",
  shopping: "text-pink-500",
  health: "text-rose-500",
  travel: "text-sky-500",
  utilities: "text-yellow-500",
  family: "text-emerald-500",
};

const bgColorMap = {
  income: "from-green-500/20 to-green-600/5",
  expense: "from-red-500/20 to-red-600/5",
  investment: "from-blue-500/20 to-blue-600/5",
  savings: "from-purple-500/20 to-purple-600/5",
  food: "from-orange-500/20 to-orange-600/5",
  housing: "from-indigo-500/20 to-indigo-600/5",
  transport: "from-cyan-500/20 to-cyan-600/5",
  shopping: "from-pink-500/20 to-pink-600/5",
  health: "from-rose-500/20 to-rose-600/5",
  travel: "from-sky-500/20 to-sky-600/5",
  utilities: "from-yellow-500/20 to-yellow-600/5",
  family: "from-emerald-500/20 to-emerald-600/5",
};

export const AnimatedFinancialIcon = ({ type, size = 24, className }: AnimatedIconProps) => {
  const Icon = iconMap[type];
  const color = colorMap[type];
  const bgGradient = bgColorMap[type];

  return (
    <motion.div
      initial={{ scale: 0, rotate: -180 }}
      animate={{ scale: 1, rotate: 0 }}
      whileHover={{ scale: 1.1, rotate: 5 }}
      transition={{ 
        type: "spring", 
        stiffness: 260, 
        damping: 20 
      }}
      className={cn(
        "relative inline-flex items-center justify-center rounded-xl p-3",
        `bg-gradient-to-br ${bgGradient}`,
        className
      )}
    >
      {/* Pulsing Background */}
      <motion.div
        className={cn(
          "absolute inset-0 rounded-xl opacity-0",
          `bg-gradient-to-br ${bgGradient}`
        )}
        animate={{
          opacity: [0, 0.5, 0],
          scale: [1, 1.1, 1],
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />
      
      {/* Icon */}
      <motion.div
        animate={{
          y: [0, -3, 0],
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      >
        <Icon 
          className={cn(color, "relative z-10")} 
          size={size}
        />
      </motion.div>

      {/* Sparkle Effect */}
      <motion.div
        className="absolute -top-1 -right-1"
        animate={{
          scale: [0, 1, 0],
          rotate: [0, 180, 360],
        }}
        transition={{
          duration: 3,
          repeat: Infinity,
          repeatDelay: 1,
        }}
      >
        <div className={cn(
          "w-2 h-2 rounded-full",
          color.replace('text-', 'bg-')
        )} />
      </motion.div>
    </motion.div>
  );
};

// Pre-built category icons
export const IncomeIcon = (props: Omit<AnimatedIconProps, 'type'>) => 
  <AnimatedFinancialIcon type="income" {...props} />;

export const ExpenseIcon = (props: Omit<AnimatedIconProps, 'type'>) => 
  <AnimatedFinancialIcon type="expense" {...props} />;

export const InvestmentIcon = (props: Omit<AnimatedIconProps, 'type'>) => 
  <AnimatedFinancialIcon type="investment" {...props} />;

export const SavingsIcon = (props: Omit<AnimatedIconProps, 'type'>) => 
  <AnimatedFinancialIcon type="savings" {...props} />;
