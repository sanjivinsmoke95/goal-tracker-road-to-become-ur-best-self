import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Page, PageHeader, EmptyState } from "@/components/ui/page";
import { Card, CardHeader } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface Point { date: string; goals: number; cf: number; lc: number; lessons: number }
interface Progress {
  range: string;
  series: Point[];
  totals: { goals_completed: number; cf_problems: number; lc_problems: number; lessons_completed: number; lessons_total: number; topics_practiced: number };
  skill_change: number | null;
}

const RANGES = ["daily", "weekly", "monthly"] as const;

export function ProgressPage() {
  const [range, setRange] = useState<string>("weekly");
  const { data, isLoading } = useQuery<Progress>({
    queryKey: ["progress", range],
    queryFn: async () => (await api.get<Progress>(`/progress?range=${range}`)).data,
  });
  const max = Math.max(1, ...(data?.series ?? []).map((p) => p.goals + p.cf + p.lc + p.lessons));

  return (
    <Page>
      <PageHeader title="Progress" subtitle="Everything here is counted from your real stored activity."
        action={
          <div className="flex rounded-md border border-zinc-200 p-0.5 dark:border-zinc-800">
            {RANGES.map((r) => (
              <button key={r} onClick={() => setRange(r)}
                className={cn("rounded px-3 py-1 text-xs capitalize", range === r ? "bg-emerald-600 text-white" : "text-zinc-500")}>{r}</button>
            ))}
          </div>
        } />
      {isLoading ? <div className="h-60 animate-pulse rounded-lg bg-zinc-100 dark:bg-zinc-800" /> : data && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            <Metric label="Goals done" value={data.totals.goals_completed} />
            <Metric label="CF solved" value={data.totals.cf_problems} />
            <Metric label="LC solved" value={data.totals.lc_problems} />
            <Metric label="Lessons" value={`${data.totals.lessons_completed}`} />
          </div>

          <Card>
            <CardHeader title="Activity" action={data.skill_change != null && (
              <span className={cn("text-xs font-medium", data.skill_change >= 0 ? "text-emerald-600" : "text-red-600")}>
                skill {data.skill_change >= 0 ? "+" : ""}{data.skill_change}
              </span>
            )} />
            <div className="p-4">
              {data.series.every((p) => p.goals + p.cf + p.lc + p.lessons === 0) ? (
                <EmptyState>No activity in this period yet.</EmptyState>
              ) : (
                <div className="flex h-40 items-end gap-1">
                  {data.series.map((p) => {
                    const total = p.goals + p.cf + p.lc + p.lessons;
                    return (
                      <div key={p.date} className="flex flex-1 flex-col items-center gap-1" title={`${p.date}: ${total}`}>
                        <div className="flex w-full flex-col justify-end" style={{ height: "100%" }}>
                          <Seg v={p.cf} max={max} className="bg-rose-500" />
                          <Seg v={p.lc} max={max} className="bg-amber-500" />
                          <Seg v={p.goals} max={max} className="bg-emerald-500" />
                          <Seg v={p.lessons} max={max} className="bg-sky-500" />
                        </div>
                        <span className="text-[9px] text-zinc-400">{p.date.slice(5)}</span>
                      </div>
                    );
                  })}
                </div>
              )}
              <div className="mt-3 flex flex-wrap gap-3 text-[11px] text-zinc-500">
                <Legend className="bg-rose-500" label="CF" /><Legend className="bg-amber-500" label="LC" />
                <Legend className="bg-emerald-500" label="Goals" /><Legend className="bg-sky-500" label="Lessons" />
              </div>
            </div>
          </Card>
        </div>
      )}
    </Page>
  );
}

function Seg({ v, max, className }: { v: number; max: number; className: string }) {
  if (v <= 0) return null;
  return <div className={cn("w-full", className)} style={{ height: `${(v / max) * 100}%`, minHeight: v > 0 ? 3 : 0 }} />;
}
function Legend({ className, label }: { className: string; label: string }) {
  return <span className="flex items-center gap-1"><span className={cn("h-2 w-2 rounded-sm", className)} /> {label}</span>;
}
function Metric({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-lg border border-zinc-200 bg-white px-3 py-2 dark:border-zinc-800 dark:bg-zinc-900">
      <div className="text-xs text-zinc-500">{label}</div>
      <div className="mt-0.5 font-mono text-lg font-semibold tabular-nums">{value}</div>
    </div>
  );
}
