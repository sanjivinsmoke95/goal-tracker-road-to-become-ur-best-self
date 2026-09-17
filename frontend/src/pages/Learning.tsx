import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { Check, ChevronRight } from "lucide-react";
import { api } from "@/lib/api";
import { Page, PageHeader } from "@/components/ui/page";
import { Card, CardHeader } from "@/components/ui/card";

interface Paths {
  paths: { id: string; title: string; topic_count: number; modules: { id: string; title: string; topics: { id: string; title: string }[] }[] }[];
  completed: string[];
  completed_count: number;
  total: number;
}

export function LearningPage() {
  const { data, isLoading } = useQuery<Paths>({
    queryKey: ["learning-paths"],
    queryFn: async () => (await api.get<Paths>("/learning/paths")).data,
  });
  const done = new Set(data?.completed ?? []);
  const pct = data && data.total ? Math.round((data.completed_count / data.total) * 100) : 0;

  return (
    <Page>
      <PageHeader title="Learning" subtitle="Frontend & backend curriculum with theory, live code, and official docs." />
      {data && (
        <div className="mb-4 rounded-lg border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-900">
          <div className="mb-2 flex justify-between text-sm">
            <span className="font-medium">Overall progress</span>
            <span className="font-mono text-zinc-500">{data.completed_count}/{data.total} topics</span>
          </div>
          <div className="h-2 overflow-hidden rounded-full bg-zinc-100 dark:bg-zinc-800">
            <div className="h-full rounded-full bg-emerald-500 transition-all" style={{ width: `${pct}%` }} />
          </div>
        </div>
      )}
      {isLoading ? <div className="h-60 animate-pulse rounded-lg bg-zinc-100 dark:bg-zinc-800" /> : (
        <div className="grid gap-4 lg:grid-cols-2">
          {data?.paths.map((p) => (
            <Card key={p.id}>
              <CardHeader title={p.title} action={<span className="text-xs text-zinc-500">{p.topic_count} topics</span>} />
              <div className="p-2">
                {p.modules.map((m) => (
                  <div key={m.id} className="mb-2">
                    <div className="px-2 py-1 text-xs font-medium uppercase tracking-wide text-zinc-400">{m.title}</div>
                    {m.topics.map((t) => (
                      <Link key={t.id} to={`/learning/topic/${t.id}`}
                        className="flex items-center gap-2.5 rounded-md px-2 py-2 text-sm hover:bg-zinc-100 dark:hover:bg-zinc-800">
                        <span className={`grid h-4 w-4 place-items-center rounded-full border ${done.has(t.id) ? "border-emerald-600 bg-emerald-600" : "border-zinc-300 dark:border-zinc-600"}`}>
                          {done.has(t.id) && <Check className="h-3 w-3 text-white" strokeWidth={3} />}
                        </span>
                        <span className="flex-1">{t.title}</span>
                        <ChevronRight className="h-4 w-4 text-zinc-300 dark:text-zinc-600" />
                      </Link>
                    ))}
                  </div>
                ))}
              </div>
            </Card>
          ))}
        </div>
      )}
    </Page>
  );
}
