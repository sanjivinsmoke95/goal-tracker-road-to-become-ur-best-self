import { useState, type FormEvent } from "react";
import { AnimatePresence, motion } from "framer-motion";
import {
  CalendarDays,
  ChevronLeft,
  ChevronRight,
  Flame,
  ListPlus,
  Repeat,
  RotateCcw,
  Trash2,
  X,
} from "lucide-react";
import {
  addDays,
  isoDay,
  useCreateRoutine,
  useDay,
  useDeleteRoutine,
  useDeleteTask,
  useDismissMissed,
  useMissed,
  useMoveMissed,
  usePasteTasks,
  useRoutines,
  useToggleRoutine,
  useToggleTask,
  WEEKDAY_LABELS,
  type Frequency,
} from "@/lib/planner";
import { CATEGORY_LABELS, type GoalCategory } from "@/lib/goals";
import { GoalRow } from "@/components/GoalRow";
import { Page, PageHeader, EmptyState } from "@/components/ui/page";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const CATEGORIES: GoalCategory[] = ["cf", "lc", "react", "backend", "cs", "other"];
const TODAY = isoDay(new Date());

function prettyDate(iso: string): string {
  return new Date(iso + "T00:00:00").toLocaleDateString(undefined, {
    weekday: "long",
    month: "short",
    day: "numeric",
  });
}

export function PlannerPage() {
  const [date, setDate] = useState(TODAY);
  const isToday = date === TODAY;

  const { data: day, isLoading } = useDay(date);
  const { data: missed = [] } = useMissed();
  const toggle = useToggleTask();
  const del = useDeleteTask();

  const total = day?.total ?? 0;
  const completed = day?.completed ?? 0;
  const pct = total ? Math.round((completed / total) * 100) : 0;

  return (
    <Page>
      <PageHeader
        title="Daily Planner"
        subtitle="Upload tasks, run your routines, and carry over what you missed."
        action={
          <motion.div
            key={day?.streak ?? 0}
            initial={{ scale: 0.9 }}
            animate={{ scale: 1 }}
            transition={{ type: "spring", stiffness: 400, damping: 20 }}
            className="inline-flex items-center gap-2 rounded-full border border-orange-200 bg-orange-50 px-3 py-1.5 text-sm font-semibold text-orange-700 dark:border-orange-500/30 dark:bg-orange-500/10 dark:text-orange-400"
          >
            <Flame className="h-4 w-4" />
            {day?.streak ?? 0} day streak
          </motion.div>
        }
      />

      {/* Missed carry-over — only when there's something to triage */}
      <AnimatePresence>{missed.length > 0 && <MissedPanel tasks={missed} />}</AnimatePresence>

      {/* Date switcher + progress */}
      <div className="mb-4 rounded-lg border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-900">
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-1">
            <button
              onClick={() => setDate(addDays(date, -1))}
              className="grid h-8 w-8 place-items-center rounded-md text-zinc-500 hover:bg-zinc-100 dark:hover:bg-zinc-800"
              aria-label="Previous day"
            >
              <ChevronLeft className="h-4 w-4" />
            </button>
            <div className="min-w-[168px] text-center">
              <div className="flex items-center justify-center gap-1.5 text-sm font-semibold">
                <CalendarDays className="h-4 w-4 text-zinc-400" />
                {isToday ? "Today" : prettyDate(date)}
              </div>
              {isToday && <div className="text-[11px] text-zinc-400">{prettyDate(date)}</div>}
            </div>
            <button
              onClick={() => setDate(addDays(date, 1))}
              className="grid h-8 w-8 place-items-center rounded-md text-zinc-500 hover:bg-zinc-100 dark:hover:bg-zinc-800"
              aria-label="Next day"
            >
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
          {!isToday && (
            <Button variant="ghost" size="sm" onClick={() => setDate(TODAY)}>
              Jump to today
            </Button>
          )}
          <span className="font-mono text-xs tabular-nums text-zinc-500">
            {completed} / {total} done
          </span>
        </div>
        <div className="mt-3 h-2 overflow-hidden rounded-full bg-zinc-100 dark:bg-zinc-800">
          <motion.div
            className="h-full rounded-full bg-emerald-500"
            initial={false}
            animate={{ width: `${pct}%` }}
            transition={{ type: "spring", stiffness: 200, damping: 30 }}
          />
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-[1fr_320px]">
        {/* Task list + add */}
        <div>
          <AddTasks date={date} />
          <div className="mt-4 space-y-2">
            {isLoading ? (
              <div className="h-12 animate-pulse rounded-lg bg-zinc-100 dark:bg-zinc-800" />
            ) : total === 0 ? (
              <EmptyState>
                <ListPlus className="mb-2 h-7 w-7 text-zinc-400" />
                Nothing planned for this day yet. Paste a list above, or add a routine.
              </EmptyState>
            ) : (
              <AnimatePresence initial={false}>
                {day!.tasks.map((t) => (
                  <GoalRow
                    key={t.id}
                    goal={t}
                    onToggle={(id) => toggle.mutate(id)}
                    onDelete={(id) => del.mutate(id)}
                    busy={toggle.isPending}
                  />
                ))}
              </AnimatePresence>
            )}
          </div>
        </div>

        {/* Routines */}
        <Routines />
      </div>
    </Page>
  );
}

/* -------------------------------------------------------------------------- */
function MissedPanel({ tasks }: { tasks: import("@/lib/goals").Goal[] }) {
  const move = useMoveMissed();
  const dismiss = useDismissMissed();
  return (
    <motion.div
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: 1, height: "auto" }}
      exit={{ opacity: 0, height: 0 }}
      className="mb-4 overflow-hidden rounded-lg border border-orange-300/60 bg-orange-50/60 dark:border-orange-500/30 dark:bg-orange-500/[0.06]"
    >
      <div className="flex items-center gap-2 border-b border-orange-200/70 px-4 py-2.5 text-sm font-semibold text-orange-800 dark:border-orange-500/20 dark:text-orange-300">
        <RotateCcw className="h-4 w-4" />
        Missed from earlier ({tasks.length})
        <span className="ml-auto text-[11px] font-normal text-orange-600/80 dark:text-orange-400/70">
          move to today or dismiss
        </span>
      </div>
      <div className="divide-y divide-orange-200/60 dark:divide-orange-500/10">
        {tasks.map((t) => (
          <div key={t.id} className="flex items-center gap-3 px-4 py-2.5">
            <span className="flex-1 truncate text-sm text-zinc-800 dark:text-zinc-100">
              {t.title}
              <span className="ml-2 text-[11px] text-zinc-400">{prettyDate(t.date)}</span>
            </span>
            <Button size="sm" onClick={() => move.mutate(t.id)} disabled={move.isPending}>
              Move to today
            </Button>
            <button
              onClick={() => dismiss.mutate(t.id)}
              className="grid h-8 w-8 place-items-center rounded-md text-zinc-400 hover:bg-orange-100 hover:text-red-500 dark:hover:bg-orange-500/10"
              aria-label="Dismiss"
              title="Dismiss (skip it)"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        ))}
      </div>
    </motion.div>
  );
}

/* -------------------------------------------------------------------------- */
function AddTasks({ date }: { date: string }) {
  const [text, setText] = useState("");
  const paste = usePasteTasks();

  function submit(e: FormEvent) {
    e.preventDefault();
    if (!text.trim()) return;
    paste.mutate({ text, date: date === TODAY ? undefined : date }, { onSuccess: () => setText("") });
  }

  return (
    <form onSubmit={submit} className="rounded-lg border border-zinc-200 bg-white p-3 dark:border-zinc-800 dark:bg-zinc-900">
      <label className="mb-1.5 flex items-center gap-1.5 text-xs font-medium text-zinc-500">
        <ListPlus className="h-3.5 w-3.5" /> Add tasks — one per line
      </label>
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        rows={3}
        placeholder={"lc: Solve 2 mediums\n[high] Revise segment trees\ncf | Div 2 virtual"}
        className="w-full resize-y rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 dark:border-zinc-700 dark:bg-zinc-950"
      />
      <div className="mt-2 flex items-center justify-between">
        <span className="text-[11px] text-zinc-400">
          Prefix with a category (<code>lc:</code>, <code>cf:</code>, <code>backend:</code>) or{" "}
          <code>[high]</code> priority.
        </span>
        <Button type="submit" size="sm" disabled={paste.isPending || !text.trim()}>
          <ListPlus className="h-4 w-4" /> Add
        </Button>
      </div>
    </form>
  );
}

/* -------------------------------------------------------------------------- */
function Routines() {
  const { data: routines = [] } = useRoutines();
  const create = useCreateRoutine();
  const toggle = useToggleRoutine();
  const del = useDeleteRoutine();

  const [title, setTitle] = useState("");
  const [category, setCategory] = useState<GoalCategory>("lc");
  const [frequency, setFrequency] = useState<Frequency>("daily");
  const [days, setDays] = useState<number[]>([]);

  function toggleDay(i: number) {
    setDays((d) => (d.includes(i) ? d.filter((x) => x !== i) : [...d, i]));
  }

  function submit(e: FormEvent) {
    e.preventDefault();
    if (!title.trim()) return;
    create.mutate(
      {
        title: title.trim(),
        category,
        priority: "medium",
        estimated_minutes: 0,
        frequency,
        days_of_week: frequency === "custom" ? days : [],
      },
      {
        onSuccess: () => {
          setTitle("");
          setDays([]);
          setFrequency("daily");
        },
      },
    );
  }

  return (
    <div className="rounded-lg border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-900">
      <div className="mb-3 flex items-center gap-2 text-sm font-semibold">
        <Repeat className="h-4 w-4 text-indigo-500" /> Recurring routines
      </div>

      <div className="space-y-1.5">
        {routines.length === 0 && (
          <p className="text-xs text-zinc-400">
            No routines yet. Add one — it auto-fills your day (e.g. “1 LeetCode daily”).
          </p>
        )}
        {routines.map((r) => (
          <div
            key={r.id}
            className={cn(
              "flex items-center gap-2 rounded-md border px-2.5 py-1.5 text-sm",
              r.active
                ? "border-zinc-200 dark:border-zinc-800"
                : "border-dashed border-zinc-200 opacity-60 dark:border-zinc-800",
            )}
          >
            <div className="min-w-0 flex-1">
              <div className="truncate">{r.title}</div>
              <div className="text-[11px] text-zinc-400">
                {CATEGORY_LABELS[r.category]} ·{" "}
                {r.frequency === "custom"
                  ? r.days_of_week.map((d) => WEEKDAY_LABELS[d]).join(" ")
                  : r.frequency}
              </div>
            </div>
            <button
              onClick={() => toggle.mutate({ id: r.id, active: !r.active })}
              className={cn(
                "rounded px-1.5 py-0.5 text-[10px] font-medium",
                r.active
                  ? "bg-emerald-500/10 text-emerald-600"
                  : "bg-zinc-200 text-zinc-500 dark:bg-zinc-800",
              )}
              title={r.active ? "Pause" : "Resume"}
            >
              {r.active ? "on" : "off"}
            </button>
            <button
              onClick={() => del.mutate(r.id)}
              className="text-zinc-300 hover:text-red-500 dark:text-zinc-600"
              aria-label="Delete routine"
            >
              <Trash2 className="h-3.5 w-3.5" />
            </button>
          </div>
        ))}
      </div>

      <form onSubmit={submit} className="mt-3 space-y-2 border-t border-zinc-100 pt-3 dark:border-zinc-800">
        <input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="New routine…"
          className="w-full rounded-md border border-zinc-300 bg-white px-2.5 py-1.5 text-sm outline-none focus:border-emerald-500 dark:border-zinc-700 dark:bg-zinc-950"
        />
        <div className="flex gap-2">
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value as GoalCategory)}
            className="flex-1 rounded-md border border-zinc-300 bg-white px-2 py-1.5 text-sm outline-none dark:border-zinc-700 dark:bg-zinc-950"
          >
            {CATEGORIES.map((c) => (
              <option key={c} value={c}>
                {CATEGORY_LABELS[c]}
              </option>
            ))}
          </select>
          <select
            value={frequency}
            onChange={(e) => setFrequency(e.target.value as Frequency)}
            className="flex-1 rounded-md border border-zinc-300 bg-white px-2 py-1.5 text-sm outline-none dark:border-zinc-700 dark:bg-zinc-950"
          >
            <option value="daily">Daily</option>
            <option value="weekdays">Weekdays</option>
            <option value="custom">Custom days</option>
          </select>
        </div>
        {frequency === "custom" && (
          <div className="flex flex-wrap gap-1">
            {WEEKDAY_LABELS.map((label, i) => (
              <button
                type="button"
                key={label}
                onClick={() => toggleDay(i)}
                className={cn(
                  "h-7 w-9 rounded text-xs font-medium",
                  days.includes(i)
                    ? "bg-emerald-600 text-white"
                    : "bg-zinc-100 text-zinc-500 dark:bg-zinc-800",
                )}
              >
                {label}
              </button>
            ))}
          </div>
        )}
        <Button
          type="submit"
          size="sm"
          className="w-full"
          disabled={create.isPending || !title.trim() || (frequency === "custom" && days.length === 0)}
        >
          <Repeat className="h-4 w-4" /> Add routine
        </Button>
      </form>
    </div>
  );
}
