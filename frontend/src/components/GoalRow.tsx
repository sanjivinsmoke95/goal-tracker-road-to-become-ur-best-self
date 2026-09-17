import { motion } from "framer-motion";
import { Check, Trash2 } from "lucide-react";
import { CATEGORY_LABELS, CATEGORY_STYLES, type Goal } from "@/lib/goals";
import { cn } from "@/lib/utils";

const PRIORITY_DOT: Record<Goal["priority"], string> = {
  high: "bg-red-500",
  medium: "bg-amber-500",
  low: "bg-zinc-400",
};

export function GoalRow({
  goal,
  onToggle,
  onDelete,
  busy,
}: {
  goal: Goal;
  onToggle: (id: string) => void;
  onDelete?: (id: string) => void;
  busy?: boolean;
}) {
  const done = goal.status === "completed";
  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 4 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, height: 0, marginTop: 0 }}
      transition={{ duration: 0.18 }}
      className={cn(
        "group flex items-center gap-3 rounded-lg border px-3 py-2.5",
        done
          ? "border-emerald-500/20 bg-emerald-500/[0.04]"
          : "border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-900",
      )}
    >
      <button
        onClick={() => onToggle(goal.id)}
        disabled={busy}
        aria-pressed={done}
        aria-label={done ? "Mark as not done" : "Mark as done"}
        className={cn(
          "grid h-5 w-5 flex-none place-items-center rounded-[6px] border transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500/50",
          done
            ? "border-emerald-600 bg-emerald-600"
            : "border-zinc-300 hover:border-emerald-500 dark:border-zinc-600",
        )}
      >
        <motion.span
          initial={false}
          animate={{ scale: done ? 1 : 0, opacity: done ? 1 : 0 }}
          transition={{ type: "spring", stiffness: 500, damping: 28 }}
        >
          <Check className="h-3.5 w-3.5 text-white" strokeWidth={3} />
        </motion.span>
      </button>

      <span className={cn("h-1.5 w-1.5 flex-none rounded-full", PRIORITY_DOT[goal.priority])} />

      <span
        className={cn(
          "flex-1 truncate text-sm",
          done ? "text-zinc-400 line-through decoration-zinc-400" : "text-zinc-800 dark:text-zinc-100",
        )}
      >
        {goal.title}
      </span>

      {goal.estimated_minutes > 0 && (
        <span className="font-mono text-[11px] text-zinc-400">{goal.estimated_minutes}m</span>
      )}

      <span className={cn("rounded border px-1.5 py-0.5 text-[10px] font-medium", CATEGORY_STYLES[goal.category])}>
        {CATEGORY_LABELS[goal.category]}
      </span>

      {onDelete && (
        <button
          onClick={() => onDelete(goal.id)}
          className="text-zinc-300 opacity-0 transition-opacity hover:text-red-500 group-hover:opacity-100 dark:text-zinc-600"
          aria-label="Delete goal"
        >
          <Trash2 className="h-4 w-4" />
        </button>
      )}
    </motion.div>
  );
}
