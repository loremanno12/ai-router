import { useLocation } from 'react-router-dom';

export default function PageNotFound() {
  const { pathname } = useLocation();
  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="text-center space-y-4">
        <h1 className="text-7xl font-light text-muted-foreground">404</h1>
        <p className="text-foreground">Page <span className="font-medium">"{pathname}"</span> not found.</p>
        <button onClick={() => window.location.href = '/'} className="px-4 py-2 text-sm border border-border rounded-lg text-foreground hover:bg-muted transition-colors">
          Go Home
        </button>
      </div>
    </div>
  );
}
