import { ArrowRight, UserPlus, Link2, BarChart } from "lucide-react";

const steps = [
  {
    icon: UserPlus,
    title: "Create Your Account",
    description: "Sign up in seconds and set up your personalized financial dashboard.",
    // step: "01",
  },
  {
    icon: Link2,
    title: "Connect Your Data",
    description: "Link your bank accounts, investments, and financial information securely.",
    // step: "02",
  },
  {
    icon: BarChart,
    title: "Get Smart Insights",
    description: "Receive AI-powered insights, track progress, and achieve your financial goals.",
    // step: "03",
  },
];

export const HowItWorks = () => {
  return (
    <section className="py-24 px-4 md:px-8">
      <div className="max-w-screen-xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-5xl font-bold mb-4">
            How <span className="gradient-text">Clarifi AI</span> Works
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Three simple steps to take control of your financial future
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 relative">
          {steps.map((step, index) => (
            <div key={index} className="relative">
              <div className="flex flex-col items-center text-center">
                <div className="mb-6 relative">
                  <div className="absolute -top-4 -left-4 text-7xl font-bold text-primary/10 dark:text-primary/5">
                  </div>
                  <div className="relative z-10 p-6 rounded-2xl bg-gradient-to-br from-primary/20 to-accent/20 backdrop-blur-sm border border-primary/20">
                    <step.icon className="w-10 h-10 text-primary" />
                  </div>
                </div>
                <h3 className="text-2xl font-semibold mb-3">{step.title}</h3>
                <p className="text-muted-foreground max-w-sm">{step.description}</p>
              </div>
              
              {index < steps.length - 1 && (
                <div className="hidden md:block absolute top-20 -right-4 z-0">
                  <ArrowRight className="w-8 h-8 text-primary/30" />
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
