import type { LucideIcon } from "lucide-react";
import { Construction } from "lucide-react";

/**
 * A useful empty state for sections that arrive in later milestones — states
 * plainly what will live here and which milestone builds it. No fake data.
 */
export function Placeholder({
  title,
  milestone,
  description,
  icon: Icon = Construction,
}: {
  title: string;
  milestone: string;
  description: string;
  icon?: LucideIcon;
}) {
  return (
    <div className="mx-auto max-w-3xl px-6 py-8">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">{title}</h1>
        <span className="rounded-full border border-zinc-300 px-2.5 py-1 font-mono text-xs text-zinc-500 dark:border-zinc-700">
          {milestone}
        </span>
      </div>

      <div className="mt-6 grid place-items-center rounded-lg border border-dashed border-zinc-300 bg-white/50 px-6 py-16 text-center dark:border-zinc-700 dark:bg-zinc-900/40">
        <Icon className="h-8 w-8 text-zinc-400" />
        <p className="mt-3 max-w-md text-sm text-zinc-500">{description}</p>
      </div>
    </div>
  );
}
