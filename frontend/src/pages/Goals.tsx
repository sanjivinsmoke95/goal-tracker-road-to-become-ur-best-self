import { useState, type FormEvent } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Flame, Plus, ListChecks } from "lucide-react";
import {
  useGoals,
  useStreak,
  useCreateGoal,
  useToggleGoal,
  useDeleteGoal,
  type GoalCategory,
  type GoalPriority,
} from "@/lib/goals";
import { GoalRow } from "@/components/GoalRow";
import { Button } from "@/components/ui/button";

const CATEGORIES: GoalCategory[] = ["cf", "lc", "react", "backend", "cs", "other"];
const PRIORITIES: GoalPriority[] = ["low", "medium", "high"];

export function GoalsPage() {
  const { data: goals = [], isLoading } = useGoals();
  const { data: streak } = useStreak();
  const createGoal = useCreateGoal();
  const toggleGoal = useToggleGoal();
  const deleteGoal = useDeleteGoal();

  const [title, setTitle] = useState("");
  const [category, setCategory] = useState<GoalCategory>("cf");
  const [priority, setPriority] = useState<GoalPriority>("medium");
  const [minutes, setMinutes] = useState("");

  const total = goals.length;
  const completed = goals.filter((g) => g.status === "completed").length;
  const pct = total ? Math.round((completed / total) * 100) : 0;
  const today = new Date().toLocaleDateString(undefined, { weekday: "long", month: "long", day: "numeric" });

  function addGoal(e: FormEvent) {
    e.preventDefault();
    if (!title.trim()) return;
    createGoal.mutate(
      { title: title.trim(), category, priority, estimated_minutes: Number(minutes) || 0 },
      { onSuccess: () => setTitle("") },
    );
  }

  return (
    <div className="mx-auto max-w-3xl px-6 py-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-semibold">Daily Goals</h1>
          <p className="text-sm text-zinc-500">{today}</p>
        </div>
        <motion.div
          key={streak?.streak ?? 0}
          initial={{ scale: 0.9 }}
          animate={{ scale: 1 }}
          transition={{ type: "spring", stiffness: 400, damping: 20 }}
          className="inline-flex items-center gap-2 rounded-full border border-orange-200 bg-orange-50 px-3 py-1.5 text-sm font-semibold text-orange-700 dark:border-orange-500/30 dark:bg-orange-500/10 dark:text-orange-400"
        >
          <Flame className="h-4 w-4" />
          {streak?.streak ?? 0} day streak
        </motion.div>
      </div>

      {/* Progress */}
      <div className="mt-5 rounded-lg border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-900">
        <div className="mb-2 flex items-center justify-between text-sm">
          <span className="font-medium text-zinc-700 dark:text-zinc-200">Today's progress</span>
          <span className="font-mono tabular-nums text-zinc-500">
            {completed} / {total} done
          </span>
        </div>
        <div className="h-2 overflow-hidden rounded-full bg-zinc-100 dark:bg-zinc-800">
          <motion.div
            className="h-full rounded-full bg-emerald-500"
            initial={false}
            animate={{ width: `${pct}%` }}
            transition={{ type: "spring", stiffness: 200, damping: 30 }}
          />
        </div>
      </div>

      {/* Add goal */}
      <form onSubmit={addGoal} className="mt-4 flex flex-wrap items-center gap-2">
        <input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Add a goal for today…"
          className="min-w-[180px] flex-1 rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 dark:border-zinc-700 dark:bg-zinc-950"
        />
        <Select value={category} onChange={(v) => setCategory(v as GoalCategory)} options={CATEGORIES} />
        <Select value={priority} onChange={(v) => setPriority(v as GoalPriority)} options={PRIORITIES} />
        <input
          value={minutes}
          onChange={(e) => setMinutes(e.target.value.replace(/\D/g, ""))}
          placeholder="min"
          inputMode="numeric"
          className="w-16 rounded-md border border-zinc-300 bg-white px-2 py-2 text-sm outline-none focus:border-emerald-500 dark:border-zinc-700 dark:bg-zinc-950"
        />
        <Button type="submit" size="sm" disabled={createGoal.isPending || !title.trim()}>
          <Plus className="h-4 w-4" /> Add
        </Button>
      </form>

      {/* List */}
      <div className="mt-4 space-y-2">
        {isLoading ? (
          <div className="h-12 animate-pulse rounded-lg bg-zinc-100 dark:bg-zinc-800" />
        ) : total === 0 ? (
          <div className="grid place-items-center rounded-lg border border-dashed border-zinc-300 py-12 text-center dark:border-zinc-700">
            <ListChecks className="h-7 w-7 text-zinc-400" />
            <p className="mt-2 text-sm text-zinc-500">No goals yet for today. Add one above to start your streak.</p>
          </div>
        ) : (
          <AnimatePresence initial={false}>
            {goals.map((g) => (
              <GoalRow
                key={g.id}
                goal={g}
                onToggle={(id) => toggleGoal.mutate(id)}
                onDelete={(id) => deleteGoal.mutate(id)}
                busy={toggleGoal.isPending}
              />
            ))}
          </AnimatePresence>
        )}
      </div>
    </div>
  );
}

function Select({ value, onChange, options }: { value: string; onChange: (v: string) => void; options: string[] }) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="rounded-md border border-zinc-300 bg-white px-2 py-2 text-sm capitalize outline-none focus:border-emerald-500 dark:border-zinc-700 dark:bg-zinc-950"
    >
      {options.map((o) => (
        <option key={o} value={o} className="capitalize">
          {o}
        </option>
      ))}
    </select>
  );
}
