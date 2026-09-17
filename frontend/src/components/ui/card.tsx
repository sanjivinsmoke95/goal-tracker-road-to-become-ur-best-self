import type { HTMLAttributes, ReactNode } from "react";
import { cn } from "@/lib/utils";

export function Card({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "rounded-lg border border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-900",
        className,
      )}
      {...props}
    />
  );
}

export function CardHeader({
  title,
  action,
  className,
}: {
  title: ReactNode;
  action?: ReactNode;
  className?: string;
}) {
  return (
    <div className={cn("flex items-center justify-between border-b border-zinc-200 px-4 py-3 dark:border-zinc-800", className)}>
      <h3 className="text-sm font-semibold text-zinc-700 dark:text-zinc-200">{title}</h3>
      {action}
    </div>
  );
}
