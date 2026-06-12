import { cn } from "../../lib/utils.js";
import { Loader as Loader2 } from "lucide-react";

export function Button({
  className,
  variant = "default",
  size = "default",
  isLoading = false,
  disabled,
  children,
  ...props
}) {
  const variants = {
    default: "bg-gradient-to-br from-[#8b5cf6] to-[#7c3aed] text-white shadow-lg hover:from-[#a78bfa] hover:to-[#8b5cf6]",
    secondary: "bg-slate-950/90 border border-[#27272a] text-white hover:bg-slate-800/95",
    outline: "border border-[#27272a] bg-transparent text-white hover:bg-[#1f1f27]",
    ghost: "bg-transparent text-muted-foreground border border-border/40 hover:bg-muted/30",
  };

  const sizes = {
    default: "px-4 py-2.5",
    sm: "px-3 py-2 text-sm",
    lg: "px-6 py-3",
  };

  return (
    <button
      className={cn(
        "rounded-xl transition-all disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-2",
        variants[variant],
        sizes[size],
        className
      )}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading && <Loader2 className="h-4 w-4 animate-spin" />}
      {children}
    </button>
  );
}
