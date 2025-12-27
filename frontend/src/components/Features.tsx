import { Wallet, TrendingUp, Target, Shield, BarChart3, Brain } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { motion } from "framer-motion";

const features = [
  {
    icon: Wallet,
    title: "Smart Financial Tracking",
    description: "Automatically track income, expenses, and cash flow across all your accounts in one unified dashboard.",
  },
  {
    icon: TrendingUp,
    title: "Investment Management",
    description: "Monitor your portfolio performance, track gains/losses, and make informed investment decisions.",
  },
  {
    icon: Target,
    title: "Goal Planning",
    description: "Set financial goals and track your progress with AI-powered recommendations to achieve them faster.",
  },
  {
    icon: Shield,
    title: "Insurance & Loans",
    description: "Manage all your insurance policies and loans in one place with EMI tracking and coverage monitoring.",
  },
  {
    icon: BarChart3,
    title: "Advanced Analytics",
    description: "Get detailed insights into spending patterns, savings rate, and financial health with interactive charts.",
  },
  {
    icon: Brain,
    title: "AI Financial Assistant",
    description: "Chat with your personal AI advisor for instant answers about your finances and smart recommendations.",
  },
];

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.1,
    },
  },
};

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 },
};

export const Features = () => {
  return (
    <section className="py-24 px-4 md:px-8 bg-muted/30">
      <div className="max-w-screen-xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl md:text-5xl font-bold mb-4">
            Everything You Need for{" "}
            <span className="gradient-text">Financial Success</span>
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Comprehensive financial management tools powered by AI to help you achieve your goals
          </p>
        </motion.div>
        
        <motion.div
          variants={container}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          {features.map((feature, index) => (
            <motion.div key={index} variants={item}>
              <Card 
                className="border-border/50 bg-card/50 backdrop-blur-sm hover:border-primary/50 transition-all duration-300 hover:shadow-lg hover:shadow-primary/10 hover:scale-105 h-full group"
              >
                <CardContent className="pt-6">
                  <motion.div
                    whileHover={{ scale: 1.1, rotate: 5 }}
                    transition={{ type: "spring", stiffness: 400, damping: 10 }}
                    className="mb-4 inline-flex p-3 rounded-xl bg-gradient-to-br from-primary/10 to-accent/10 group-hover:from-primary/20 group-hover:to-accent/20"
                  >
                    <feature.icon className="w-6 h-6 text-primary" />
                  </motion.div>
                  <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                  <p className="text-muted-foreground">{feature.description}</p>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
};
