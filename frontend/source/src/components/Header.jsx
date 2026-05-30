export default function Header() {
  return (
    <header className="w-full border-b border-border px-6 py-4">
      <div className="max-w-5xl mx-auto flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 rounded-lg bg-primary/20 flex items-center justify-center">
            <div className="h-4 w-4 rounded-sm bg-primary" />
          </div>
          <h1 className="text-xl font-semibold text-foreground">AI Router</h1>
        </div>

        <div className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse-glow" />
          <span className="text-sm text-muted-foreground">System ready</span>
        </div>
      </div>
    </header>
  );
}
