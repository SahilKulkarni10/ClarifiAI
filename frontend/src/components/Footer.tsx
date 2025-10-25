import { Sparkles } from "lucide-react";

const footerLinks = {
  product: [
    { name: "Dashboard", href: "/dashboard" },
    { name: "Investments", href: "/investments" },
    { name: "Analytics", href: "/analytics" },
    { name: "AI Assistant", href: "/chat" },
  ],
  resources: [
    { name: "Help Center", href: "#help" },
    { name: "Financial Tips", href: "#tips" },
    { name: "API Docs", href: "#api" },
    { name: "Community", href: "#community" },
  ],
  company: [
    { name: "About Us", href: "#about" },
    { name: "Blog", href: "#blog" },
    { name: "Careers", href: "#careers" },
    { name: "Contact", href: "#contact" },
  ],
  legal: [
    { name: "Privacy Policy", href: "#privacy" },
    { name: "Terms of Service", href: "#terms" },
    { name: "Security", href: "#security" },
    { name: "Data Protection", href: "#data" },
  ],
};

export const Footer = () => {
  return (
    <footer className="border-t border-border/40 bg-muted/30">
      <div className="max-w-screen-xl mx-auto px-4 py-12 md:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          <div className="col-span-1">
            <div className="flex items-center gap-2 mb-4">
              <div className="p-2 rounded-lg bg-gradient-to-br from-primary to-accent">
                <Sparkles className="w-5 h-5 text-primary-foreground" />
              </div>
              <span className="text-xl font-bold">Clarifi AI</span>
            </div>
            <p className="text-sm text-muted-foreground">
              AI-powered financial management platform. Take control of your financial future with intelligent insights.
            </p>
          </div>
          
          <div>
            <h3 className="font-semibold mb-4">Product</h3>
            <ul className="space-y-2">
              {footerLinks.product.map((link) => (
                <li key={link.name}>
                  <a 
                    href={link.href}
                    className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                  >
                    {link.name}
                  </a>
                </li>
              ))}
            </ul>
          </div>
          
          <div>
            <h3 className="font-semibold mb-4">Resources</h3>
            <ul className="space-y-2">
              {footerLinks.resources.map((link) => (
                <li key={link.name}>
                  <a 
                    href={link.href}
                    className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                  >
                    {link.name}
                  </a>
                </li>
              ))}
            </ul>
          </div>
          
          <div>
            <h3 className="font-semibold mb-4">Legal</h3>
            <ul className="space-y-2">
              {footerLinks.legal.map((link) => (
                <li key={link.name}>
                  <a 
                    href={link.href}
                    className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                  >
                    {link.name}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        </div>
        
        <div className="pt-8 border-t border-border/40 text-center text-sm text-muted-foreground">
          <p>&copy; {new Date().getFullYear()} Clarifi AI. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
};
