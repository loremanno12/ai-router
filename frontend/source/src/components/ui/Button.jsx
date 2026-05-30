import { cn } from "@/lib/utils";
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
    default: "bg-primary text-primary-foreground hover:bg-primary/90",
    secondary: "bg-secondary/60 border border-border text-foreground hover:bg-secondary/80",
    outline: "border border-border bg-transparent hover:bg-muted/40",
    ghost: "hover:bg-muted/40",
  };

  const sizes = {
    default: "px-4 py-2.5",
    sm: "px-3 py-2 text-sm",
    lg: "px-6 py-3",
  };

  return (
    <button
      className={cn(
        "rounded-lg transition-all disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-2",
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
