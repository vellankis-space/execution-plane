import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "@/hooks/use-toast";
import { useAuth } from "@/hooks/use-auth";
import { Sparkles, ArrowRight } from "lucide-react";

export function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      await login(email, password);
      toast({
        title: "Login successful",
        description: "Welcome back!",
      });
      navigate("/");
    } catch (error: any) {
      toast({
        title: "Login failed",
        description: error.message || "Invalid email or password",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-background via-background to-primary/5">
      <div className="w-full max-w-md px-4">
        <Card className="border-border/50 bg-card/80 backdrop-blur-sm shadow-2xl">
          <div className="p-8">
            {/* Logo and Title */}
            <div className="flex flex-col items-center mb-8">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary to-primary/70 flex items-center justify-center shadow-lg shadow-primary/25 mb-4">
                <Sparkles className="w-8 h-8 text-primary-foreground" />
              </div>
              <h1 className="text-3xl font-bold bg-gradient-to-br from-foreground to-foreground/70 bg-clip-text text-transparent">
                AI Platform
              </h1>
              <p className="text-muted-foreground mt-2 text-center">
                Sign in to access your orchestration suite
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">
              <div className="space-y-2">
                <Label htmlFor="email" className="text-sm font-medium">
                  Email
                </Label>
                <Input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  autoComplete="email"
                  className="h-11 border-border/50 focus:border-primary transition-colors"
                  placeholder="you@example.com"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="password" className="text-sm font-medium">
                  Password
                </Label>
                <Input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  autoComplete="current-password"
                  className="h-11 border-border/50 focus:border-primary transition-colors"
                  placeholder="••••••••"
                />
              </div>

              <Button 
                type="submit" 
                className="w-full h-11 bg-gradient-to-r from-primary to-primary/90 hover:shadow-lg hover:shadow-primary/25 transition-all shine-effect group" 
                disabled={isLoading}
              >
                {isLoading ? (
                  <span className="flex items-center gap-2">
                    <div className="w-4 h-4 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin" />
                    Signing in...
                  </span>
                ) : (
                  <span className="flex items-center gap-2">
                    Sign In
                    <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                  </span>
                )}
              </Button>
            </form>

            <div className="mt-6 text-center">
              <p className="text-xs text-muted-foreground">
                Secure authentication powered by your organization
              </p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}

