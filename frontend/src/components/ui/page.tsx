import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

export function Page({ children, className }: { children: ReactNode; className?: string }) {
  return <div className={cn("mx-auto max-w-5xl px-6 py-8", className)}>{children}</div>;
}

export function PageHeader({ title, subtitle, action }: { title: string; subtitle?: string; action?: ReactNode }) {
  return (
    <div className="mb-6 flex flex-wrap items-start justify-between gap-3">
      <div>
        <h1 className="text-xl font-semibold">{title}</h1>
        {subtitle && <p className="mt-0.5 text-sm text-zinc-500">{subtitle}</p>}
      </div>
      {action}
    </div>
  );
}

export function EmptyState({ children }: { children: ReactNode }) {
  return (
    <div className="grid place-items-center rounded-lg border border-dashed border-zinc-300 px-6 py-12 text-center text-sm text-zinc-500 dark:border-zinc-700">
      {children}
    </div>
  );
}

/** Small provenance chips so estimates are never mistaken for facts. */
export function Tag({ kind }: { kind: "data" | "inference" | "recommendation" }) {
  const map = {
    data: "border-sky-300 text-sky-600 dark:border-sky-500/40 dark:text-sky-400",
    inference: "border-violet-300 text-violet-600 dark:border-violet-500/40 dark:text-violet-400",
    recommendation: "border-emerald-300 text-emerald-600 dark:border-emerald-500/40 dark:text-emerald-400",
  };
  return (
    <span className={cn("rounded border px-1.5 py-0.5 font-mono text-[10px] uppercase", map[kind])}>{kind}</span>
  );
}
