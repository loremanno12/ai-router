import { cn } from "../../lib/utils.js";

export function Textarea({
  className,
  disabled,
  ...props
}) {
  return (
    <textarea
      className={cn(
        "w-full min-h-40 p-4 rounded-md bg-[#1c1c22]/90 border border-[#27272a]",
        "text-foreground placeholder:text-muted-foreground",
        "focus:outline-none focus:ring-2 focus:ring-[#8b5cf6]/50 focus:border-[#8b5cf6]/50",
        "resize-none transition-all disabled:opacity-50",
        className
      )}
      disabled={disabled}
      {...props}
    />
  );
}
