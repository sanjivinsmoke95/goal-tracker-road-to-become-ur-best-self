import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Page, PageHeader, EmptyState, Tag } from "@/components/ui/page";
import { Card, CardHeader } from "@/components/ui/card";

interface Topic { tag: string; attempts: number; solved: number; score: number | null; band: string }
interface Skills {
  estimated_rating: number | null;
  confidence: number;
  recommended_range: number[] | null;
  recent_success_rate: number | null;
  total_solved: number;
  total_attempts: number;
  strengths: string[];
  reinforce: string[];
  topics: Topic[];
  available: boolean;
}

const BAND: Record<string, { label: string; color: string; bar: string }> = {
  strong: { label: "Strong", color: "text-emerald-600 dark:text-emerald-400", bar: "bg-emerald-500" },
  developing: { label: "Developing", color: "text-sky-600 dark:text-sky-400", bar: "bg-sky-500" },
  needs_reinforcement: { label: "Needs reinforcement", color: "text-amber-600 dark:text-amber-400", bar: "bg-amber-500" },
  insufficient_data: { label: "Insufficient data", color: "text-zinc-400", bar: "bg-zinc-300 dark:bg-zinc-600" },
};

export function SkillsPage() {
  const { data, isLoading } = useQuery<Skills>({
    queryKey: ["skills"],
    queryFn: async () => (await api.get<Skills>("/skills")).data,
  });

  return (
    <Page>
      <PageHeader title="Skill Analysis" subtitle="Estimated from your real submissions — never from problem counts alone." action={<Tag kind="inference" />} />
      {isLoading ? (
        <div className="h-60 animate-pulse rounded-lg bg-zinc-100 dark:bg-zinc-800" />
      ) : !data?.available ? (
        <EmptyState>Not enough data yet. Connect Codeforces and sync to build your skill profile.</EmptyState>
      ) : (
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            <Metric label="Est. level" value={data.estimated_rating ?? "—"} sub={data.recommended_range ? `range ${data.recommended_range[0]}–${data.recommended_range[1]}` : ""} />
            <Metric label="Confidence" value={`${Math.round(data.confidence * 100)}%`} />
            <Metric label="Recent success" value={data.recent_success_rate != null ? `${Math.round(data.recent_success_rate * 100)}%` : "—"} />
            <Metric label="Solved / tried" value={`${data.total_solved}/${data.total_attempts}`} />
          </div>

          <Card>
            <CardHeader title="Topic matrix" action={<span className="text-xs text-zinc-500">score = success × difficulty, recent-weighted</span>} />
            <div className="space-y-2 p-4">
              {data.topics.length === 0 ? <EmptyState>No topic data yet.</EmptyState> : data.topics.map((t) => {
                const b = BAND[t.band] || BAND.insufficient_data;
                return (
                  <div key={t.tag} className="flex items-center gap-3">
                    <span className="w-40 shrink-0 truncate text-sm">{t.tag}</span>
                    <div className="h-2 flex-1 overflow-hidden rounded-full bg-zinc-100 dark:bg-zinc-800">
                      {t.score != null && <div className={`h-full rounded-full ${b.bar}`} style={{ width: `${t.score}%` }} />}
                    </div>
                    <span className="w-10 text-right font-mono text-xs tabular-nums text-zinc-500">{t.score != null ? Math.round(t.score) : "—"}</span>
                    <span className={`w-36 shrink-0 text-right text-xs ${b.color}`}>{b.label}</span>
                  </div>
                );
              })}
            </div>
          </Card>
        </div>
      )}
    </Page>
  );
}

function Metric({ label, value, sub }: { label: string; value: string | number; sub?: string }) {
  return (
    <div className="rounded-lg border border-zinc-200 bg-white px-3 py-2 dark:border-zinc-800 dark:bg-zinc-900">
      <div className="text-xs text-zinc-500">{label}</div>
      <div className="mt-0.5 font-mono text-lg font-semibold tabular-nums">{value}</div>
      {sub && <div className="text-[11px] text-zinc-400">{sub}</div>}
    </div>
  );
}
