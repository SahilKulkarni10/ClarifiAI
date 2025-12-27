import { Navigation } from "@/components/Navigation";
import { HeroSection } from "@/components/ui/hero-section-dark";
import { Features } from "@/components/Features";
import { HowItWorks } from "@/components/HowItWorks";
import { CTA } from "@/components/CTA";
import { Footer } from "@/components/Footer";
import { motion } from "framer-motion";

const Index = () => {
  return (
    <div className="min-h-screen">
      <Navigation />
      <main className="pt-16">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6 }}
        >
          <HeroSection
            title="AI-Powered Financial Clarity"
            subtitle={{
              regular: "Master your finances with ",
              gradient: "intelligent insights",
            }}
            description="Clarifi AI brings all your financial data together in one place. Track income, expenses, investments, loans, insurance, and goals with AI-powered analytics that help you make smarter money decisions."
            ctaText="Start Managing Your Finances"
            ctaHref="/dashboard"
            gridOptions={{
              angle: 65,
              opacity: 0.4,
              cellSize: 50,
              lightLineColor: "#4a4a4a",
              darkLineColor: "#2a2a2a",
            }}
          />
        </motion.div>
        
        <motion.div
          id="features"
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.6 }}
        >
          <Features />
        </motion.div>
        
        <motion.div
          id="how-it-works"
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.6 }}
        >
          <HowItWorks />
        </motion.div>
        
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.6 }}
        >
          <CTA />
        </motion.div>
        
        <Footer />
      </main>
    </div>
  );
};

export default Index;
