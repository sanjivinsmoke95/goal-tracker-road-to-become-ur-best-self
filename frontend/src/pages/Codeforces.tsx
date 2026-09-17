import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AxiosError } from "axios";
import { RefreshCw, ExternalLink } from "lucide-react";
import { api } from "@/lib/api";
import { Page, PageHeader, EmptyState } from "@/components/ui/page";
import { Card, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

interface CfProfile { handle: string; rating: number | null; max_rating: number | null; rank: string | null; last_synced_at: string | null }
interface Sub { id: string; external_id: string; problem_id: string | null; verdict: string; language: string; submitted_at: string; problem_rating: number | null; problem_tags: string[] }

const VERDICT_STYLE: Record<string, string> = {
  OK: "text-emerald-600 dark:text-emerald-400",
  WRONG_ANSWER: "text-red-600 dark:text-red-400",
  TIME_LIMIT_EXCEEDED: "text-amber-600 dark:text-amber-400",
};

export function CodeforcesPage() {
  const qc = useQueryClient();
  const [handle, setHandle] = useState("");
  const [error, setError] = useState<string | null>(null);

  const { data: profile, isLoading } = useQuery<CfProfile | null>({
    queryKey: ["cf-profile"],
    queryFn: async () => (await api.get<CfProfile | null>("/codeforces/profile")).data,
  });
  const { data: subs = [] } = useQuery<Sub[]>({
    queryKey: ["cf-subs"],
    queryFn: async () => (await api.get<Sub[]>("/codeforces/submissions?limit=50")).data,
    enabled: !!profile,
  });

  const connect = useMutation({
    mutationFn: async (h: string) => (await api.post("/platforms/codeforces/connect", { handle: h })).data,
    onSuccess: () => { qc.invalidateQueries(); setError(null); },
    onError: (e) => setError((e as AxiosError<{ detail?: string }>).response?.data?.detail || "Could not connect."),
  });
  const sync = useMutation({
    mutationFn: async () => (await api.post("/platforms/codeforces/sync")).data,
    onSuccess: () => qc.invalidateQueries(),
  });

  if (isLoading) return <Page><div className="h-40 animate-pulse rounded-lg bg-zinc-100 dark:bg-zinc-800" /></Page>;

  if (!profile) {
    return (
      <Page>
        <PageHeader title="Codeforces" subtitle="Connect your handle to sync your rating, submissions, and solved problems." />
        <Card className="max-w-md">
          <div className="p-5">
            <label className="mb-1 block text-xs font-medium text-zinc-500">Codeforces handle</label>
            <div className="flex gap-2">
              <input value={handle} onChange={(e) => setHandle(e.target.value)} placeholder="e.g. tourist"
                className="flex-1 rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm outline-none focus:border-emerald-500 dark:border-zinc-700 dark:bg-zinc-950" />
              <Button onClick={() => handle.trim() && connect.mutate(handle.trim())} disabled={connect.isPending}>
                {connect.isPending ? "Connecting…" : "Connect"}
              </Button>
            </div>
            {error && <p className="mt-2 text-sm text-red-600 dark:text-red-400">{error}</p>}
            <p className="mt-3 text-xs text-zinc-500">Uses the public Codeforces API — no password needed. Note: the API doesn't expose submission source code.</p>
          </div>
        </Card>
      </Page>
    );
  }

  return (
    <Page>
      <PageHeader
        title="Codeforces"
        subtitle={`Connected as ${profile.handle}`}
        action={<Button variant="secondary" size="sm" onClick={() => sync.mutate()} disabled={sync.isPending}>
          <RefreshCw className={`h-4 w-4 ${sync.isPending ? "animate-spin" : ""}`} /> Sync
        </Button>}
      />
      <div className="mb-4 grid grid-cols-2 gap-3 sm:grid-cols-4">
        <Stat label="Rating" value={profile.rating ?? "—"} />
        <Stat label="Max rating" value={profile.max_rating ?? "—"} />
        <Stat label="Rank" value={profile.rank ?? "—"} />
        <Stat label="Submissions" value={subs.length} />
      </div>
      {sync.data && <p className="mb-3 text-xs text-emerald-600">Synced · {(sync.data as { new_submissions: number }).new_submissions} new submissions.</p>}

      <Card>
        <CardHeader title="Recent submissions" />
        {subs.length === 0 ? <div className="p-4"><EmptyState>No submissions yet — hit Sync.</EmptyState></div> : (
          <div className="divide-y divide-zinc-100 dark:divide-zinc-800">
            {subs.slice(0, 25).map((s) => (
              <div key={s.id} className="flex items-center gap-3 px-4 py-2 text-sm">
                <span className={`w-32 shrink-0 truncate font-mono text-xs ${VERDICT_STYLE[s.verdict] || "text-zinc-500"}`}>{s.verdict}</span>
                <span className="w-14 shrink-0 font-mono text-xs text-zinc-500">{s.problem_rating ?? "—"}</span>
                <span className="flex-1 truncate text-xs text-zinc-500">{(s.problem_tags || []).slice(0, 3).join(", ")}</span>
                <a href={`https://codeforces.com/problemset/problem/${s.problem_id?.split(":")[1]?.slice(0, -1)}/${s.problem_id?.slice(-1)}`}
                   target="_blank" rel="noreferrer" className="text-zinc-400 hover:text-emerald-500"><ExternalLink className="h-3.5 w-3.5" /></a>
              </div>
            ))}
          </div>
        )}
      </Card>
    </Page>
  );
}

function Stat({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-lg border border-zinc-200 bg-white px-3 py-2 dark:border-zinc-800 dark:bg-zinc-900">
      <div className="text-xs text-zinc-500">{label}</div>
      <div className="mt-0.5 font-mono text-lg font-semibold tabular-nums">{value}</div>
    </div>
  );
}
