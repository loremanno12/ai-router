import { cn } from "@/lib/utils";

export function Textarea({
  className,
  disabled,
  ...props
}) {
  return (
    <textarea
      className={cn(
        "w-full min-h-40 p-4 rounded-xl bg-muted/40 border border-border",
        "text-foreground placeholder:text-muted-foreground",
        "focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50",
        "resize-none transition-all disabled:opacity-50",
        className
      )}
      disabled={disabled}
      {...props}
    />
  );
}
