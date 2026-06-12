import { useLocation } from "react-router-dom";
import { Button } from "@/components/ui/Button";

export default function PageNotFound() {
  const { pathname } = useLocation();

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="text-center space-y-6">
        <h1 className="text-8xl font-light text-muted-foreground">404</h1>
        <div className="space-y-2">
          <p className="text-foreground">
            Page <span className="font-medium text-primary">"{pathname}"</span> not found.
          </p>
          <p className="text-sm text-muted-foreground">
            The page you're looking for doesn't exist or has been moved.
          </p>
        </div>
        <Button onClick={() => (window.location.href = "/")}>
          Go Home
        </Button>
      </div>
    </div>
  );
}
