import { useQuery } from "@tanstack/react-query";
import { ExternalLink, Swords, Code2 } from "lucide-react";
import { api } from "@/lib/api";
import { Page, PageHeader, EmptyState, Tag } from "@/components/ui/page";
import { Card, CardHeader } from "@/components/ui/card";

interface Daily {
  platform: string;
  problem: { id: string; name: string; rating: number | null; difficulty: string | null; tags: string[]; url: string } | null;
  target_rating: number | null;
  score: number;
  reason: { components?: Record<string, number>; top_reason?: string };
  explanation: string;
}
interface Potd {
  codeforces: Daily | null;
  leetcode: Daily | null;
}

export function ProblemOfTheDayPage() {
  const { data, isLoading } = useQuery<Potd>({
    queryKey: ["potd"],
    queryFn: async () => (await api.get<Potd>("/problems/today")).data,
  });

  return (
    <Page>
      <PageHeader title="Problem of the Day" subtitle="One useful challenge per platform, chosen at your current level." />
      <div className="grid gap-4 lg:grid-cols-2">
        <PotdCard title="Codeforces" icon={Swords} daily={data?.codeforces} loading={isLoading} />
        <PotdCard title="LeetCode" icon={Code2} daily={data?.leetcode} loading={isLoading} />
      </div>
    </Page>
  );
}

function PotdCard({ title, icon: Icon, daily, loading }: { title: string; icon: typeof Swords; daily?: Daily | null; loading: boolean }) {
  return (
    <Card>
      <CardHeader title={<span className="flex items-center gap-2"><Icon className="h-4 w-4" /> {title}</span>} action={<Tag kind="recommendation" />} />
      <div className="p-4">
        {loading ? (
          <div className="h-40 animate-pulse rounded-md bg-zinc-100 dark:bg-zinc-800" />
        ) : !daily || !daily.problem ? (
          <EmptyState>Connect {title} and sync to get a Problem of the Day.</EmptyState>
        ) : (
          <div>
            <div className="flex items-start justify-between gap-3">
              <div>
                <div className="text-base font-semibold">{daily.problem.name}</div>
                <div className="mt-1 flex flex-wrap items-center gap-2 text-xs text-zinc-500">
                  {daily.problem.rating != null && <span className="rounded bg-zinc-100 px-1.5 py-0.5 font-mono dark:bg-zinc-800">{daily.problem.rating}</span>}
                  {daily.problem.difficulty && <span className="rounded bg-zinc-100 px-1.5 py-0.5 dark:bg-zinc-800">{daily.problem.difficulty}</span>}
                  {daily.problem.tags.slice(0, 4).map((t) => (
                    <span key={t} className="rounded bg-zinc-100 px-1.5 py-0.5 dark:bg-zinc-800">{t}</span>
                  ))}
                </div>
              </div>
              <a href={daily.problem.url} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1.5 rounded-md bg-emerald-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-emerald-500">
                Solve <ExternalLink className="h-3.5 w-3.5" />
              </a>
            </div>

            <div className="mt-3 rounded-md bg-violet-50 px-3 py-2 text-sm text-violet-800 dark:bg-violet-500/10 dark:text-violet-300">
              <div className="mb-0.5 flex items-center gap-1.5 text-xs font-medium"><Tag kind="inference" /> why this problem</div>
              {daily.explanation}
            </div>

            {daily.reason.components && (
              <div className="mt-3 space-y-1.5">
                {Object.entries(daily.reason.components).map(([k, v]) => (
                  <div key={k} className="flex items-center gap-2">
                    <span className="w-40 shrink-0 text-xs text-zinc-500">{k.replace(/_/g, " ")}</span>
                    <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-zinc-100 dark:bg-zinc-800">
                      <div className="h-full rounded-full bg-emerald-500" style={{ width: `${Math.round(Math.max(0, Math.min(1, v)) * 100)}%` }} />
                    </div>
                    <span className="w-9 text-right font-mono text-[11px] tabular-nums text-zinc-500">{v.toFixed(2)}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </Card>
  );
}
