import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";

export const CTA = () => {
  return (
    <section className="py-24 px-4 md:px-8 relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-accent/5 to-transparent" />
      <div className="max-w-screen-xl mx-auto relative z-10">
        <div className="text-center max-w-3xl mx-auto">
          <h2 className="text-3xl md:text-5xl font-bold mb-6">
            Ready to Take Control of Your <span className="gradient-text">Financial Future</span>?
          </h2>
          <p className="text-lg text-muted-foreground mb-8">
            Join thousands of users who are already managing their finances smarter with Clarifi AI's intelligent platform.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <span className="relative inline-block overflow-hidden rounded-full p-[1.5px]">
              <span className="absolute inset-[-1000%] animate-[spin_2s_linear_infinite] bg-[conic-gradient(from_90deg_at_50%_50%,#60A5FA_0%,#3B82F6_50%,#60A5FA_100%)]" />
              <div className="inline-flex h-full w-full cursor-pointer items-center justify-center rounded-full bg-background text-xs font-medium backdrop-blur-3xl">
                <Button 
                  size="lg"
                  className="rounded-full bg-gradient-to-tr from-zinc-300/20 via-blue-400/30 to-transparent dark:from-zinc-300/5 dark:via-blue-400/20 border-input border-[1px] hover:bg-gradient-to-tr hover:from-zinc-300/30 hover:via-blue-400/40 hover:to-transparent dark:hover:from-zinc-300/10 dark:hover:via-blue-400/30"
                  onClick={() => window.location.href = '/register'}
                >
                  Get Started Free
                  <ArrowRight className="ml-2 w-4 h-4" />
                </Button>
              </div>
            </span>
            
            <Button 
              size="lg" 
              variant="outline"
              className="rounded-full"
              onClick={() => window.location.href = '/login'}
            >
              Sign In
            </Button>
          </div>
          
          <p className="mt-6 text-sm text-muted-foreground">
            No credit card required • Secure and encrypted • Start in minutes
          </p>
        </div>
      </div>
    </section>
  );
};
