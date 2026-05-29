export default function UserNotRegisteredError() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="text-center space-y-3">
        <h2 className="text-xl font-semibold text-foreground">Access Denied</h2>
        <p className="text-muted-foreground">You are not registered for this app.</p>
      </div>
    </div>
  );
}
