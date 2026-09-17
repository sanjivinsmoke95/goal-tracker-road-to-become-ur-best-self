import { useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Sparkles, Upload, RefreshCw } from "lucide-react";
import { api } from "@/lib/api";
import { Page, PageHeader, EmptyState } from "@/components/ui/page";
import { Card, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

interface Task { category: string; title: string; done?: boolean }
interface PlanDay { id: string; day_number: number; date: string; tasks: Task[] }
interface Plan { id: string; title: string; goal: string; duration_days: number; source: string; days: PlanDay[] }

const CAT_COLOR: Record<string, string> = {
  cf: "text-rose-500", lc: "text-amber-500", react: "text-sky-500", backend: "text-violet-500", cs: "text-teal-500", other: "text-zinc-400",
};

export function PlansPage() {
  const qc = useQueryClient();
  const fileRef = useRef<HTMLInputElement>(null);
  const [goal, setGoal] = useState("Learn React + Backend + DSA");
  const [duration, setDuration] = useState("30");

  const { data: plan, isLoading } = useQuery<Plan | null>({
    queryKey: ["plan-current"],
    queryFn: async () => (await api.get<Plan | null>("/plans/current")).data,
  });
  const invalidate = () => qc.invalidateQueries({ queryKey: ["plan-current"] });

  const generate = useMutation({
    mutationFn: async () => (await api.post("/plans/generate", { goal, duration_days: Number(duration) || 30, hours_per_day: 3 })).data,
    onSuccess: invalidate,
  });
  const upload = useMutation({
    mutationFn: async (file: File) => { const fd = new FormData(); fd.append("file", file); return (await api.post("/plans/upload", fd)).data; },
    onSuccess: invalidate,
  });
  const adapt = useMutation({
    mutationFn: async () => (await api.post(`/plans/${plan!.id}/adapt`)).data,
    onSuccess: invalidate,
  });
  const toggleTask = useMutation({
    mutationFn: async ({ day, tasks }: { day: PlanDay; tasks: Task[] }) =>
      (await api.patch(`/plans/${plan!.id}/days/${day.day_number}`, { tasks })).data,
    onSuccess: invalidate,
  });

  return (
    <Page>
      <PageHeader title="Learning Plans" subtitle="Upload a schedule or generate one — then let it adapt to your progress."
        action={plan && <Button size="sm" variant="secondary" onClick={() => adapt.mutate()} disabled={adapt.isPending}>
          <RefreshCw className={`h-4 w-4 ${adapt.isPending ? "animate-spin" : ""}`} /> Adapt to progress
        </Button>} />

      <div className="mb-4 grid gap-3 sm:grid-cols-2">
        <Card>
          <CardHeader title="Generate a plan" />
          <div className="space-y-2 p-4">
            <input value={goal} onChange={(e) => setGoal(e.target.value)} placeholder="Your goal"
              className="w-full rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-950" />
            <div className="flex gap-2">
              <input value={duration} onChange={(e) => setDuration(e.target.value.replace(/\D/g, ""))} placeholder="days"
                className="w-24 rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-950" />
              <Button onClick={() => generate.mutate()} disabled={generate.isPending}><Sparkles className="h-4 w-4" /> Generate</Button>
            </div>
          </div>
        </Card>
        <Card>
          <CardHeader title="Upload a schedule" />
          <div className="p-4">
            <input ref={fileRef} type="file" accept=".csv,.json" className="hidden"
              onChange={(e) => e.target.files?.[0] && upload.mutate(e.target.files[0])} />
            <Button variant="secondary" onClick={() => fileRef.current?.click()} disabled={upload.isPending}>
              <Upload className="h-4 w-4" /> {upload.isPending ? "Parsing…" : "Choose CSV / JSON"}
            </Button>
            <p className="mt-2 text-xs text-zinc-500">Columns: Day, Category, Topic, Task, Duration. Converted into real plan days.</p>
          </div>
        </Card>
      </div>

      {isLoading ? <div className="h-40 animate-pulse rounded-lg bg-zinc-100 dark:bg-zinc-800" /> : !plan ? (
        <EmptyState>No active plan. Generate or upload one above.</EmptyState>
      ) : (
        <Card>
          <CardHeader title={plan.title} action={<span className="text-xs text-zinc-500">{plan.days.length} days · {plan.source}</span>} />
          <div className="max-h-[480px] divide-y divide-zinc-100 overflow-y-auto dark:divide-zinc-800">
            {plan.days.map((d) => (
              <div key={d.id} className="px-4 py-3">
                <div className="mb-1.5 text-xs font-medium text-zinc-500">Day {d.day_number} · {d.date}</div>
                <div className="space-y-1">
                  {d.tasks.map((t, i) => (
                    <label key={i} className="flex cursor-pointer items-center gap-2 text-sm">
                      <input type="checkbox" checked={!!t.done} className="h-4 w-4 accent-emerald-600"
                        onChange={() => { const tasks = d.tasks.map((x, j) => j === i ? { ...x, done: !x.done } : x); toggleTask.mutate({ day: d, tasks }); }} />
                      <span className={`font-mono text-[10px] uppercase ${CAT_COLOR[t.category] || CAT_COLOR.other}`}>{t.category}</span>
                      <span className={t.done ? "text-zinc-400 line-through" : ""}>{t.title}</span>
                    </label>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}
      {adapt.data != null && <p className="mt-2 text-xs text-emerald-600">Adapted · {(adapt.data as { redistributed_tasks: number }).redistributed_tasks} unfinished tasks redistributed.</p>}
    </Page>
  );
}
