import { useLocation } from "react-router-dom";
import { useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Home, ArrowLeft } from "lucide-react";
import { useNavigate } from "react-router-dom";

const NotFound = () => {
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    console.error("404 Error: User attempted to access non-existent route:", location.pathname);
  }, [location.pathname]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4 bg-gradient-to-br from-background via-background to-primary/5">
      <div className="text-center max-w-md">
        <div className="relative mb-8">
          <h1 className="text-9xl font-bold bg-gradient-to-br from-primary to-primary/50 bg-clip-text text-transparent">
            404
          </h1>
          <div className="absolute inset-0 blur-3xl bg-primary/20 -z-10" />
        </div>
        <h2 className="text-3xl font-bold mb-3">Page Not Found</h2>
        <p className="text-muted-foreground mb-8 text-lg">
          The page you're looking for doesn't exist or has been moved.
        </p>
        <div className="flex gap-3 justify-center">
          <Button 
            variant="outline" 
            onClick={() => navigate(-1)}
            className="gap-2"
          >
            <ArrowLeft className="w-4 h-4" />
            Go Back
          </Button>
          <Button 
            onClick={() => navigate("/")} 
            className="gap-2 bg-gradient-to-r from-primary to-primary/90 shine-effect"
          >
            <Home className="w-4 h-4" />
            Back to Home
          </Button>
        </div>
      </div>
    </div>
  );
};

export default NotFound;
