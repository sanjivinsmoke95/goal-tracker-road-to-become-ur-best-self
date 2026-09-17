import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AxiosError } from "axios";
import { ExternalLink } from "lucide-react";
import { api } from "@/lib/api";
import { Page, PageHeader, EmptyState } from "@/components/ui/page";
import { Card, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

interface LcProfile { connected: boolean; handle: string | null; solved: number; estimated_level: string | null }
interface Problem { id: string; external_id: string; name: string; difficulty: string | null; tags: string[]; url: string }

const DIFF: Record<string, string> = { Easy: "text-emerald-600", Medium: "text-amber-600", Hard: "text-red-600" };

export function LeetCodePage() {
  const qc = useQueryClient();
  const [handle, setHandle] = useState("");
  const [error, setError] = useState<string | null>(null);
  const { data: profile } = useQuery<LcProfile>({ queryKey: ["lc-profile"], queryFn: async () => (await api.get<LcProfile>("/leetcode/profile")).data });
  const { data: problems = [] } = useQuery<Problem[]>({ queryKey: ["lc-problems"], queryFn: async () => (await api.get<Problem[]>("/leetcode/problems?limit=100")).data, enabled: !!profile?.connected });

  const connect = useMutation({
    mutationFn: async (h: string) => (await api.post("/platforms/leetcode/connect", { handle: h })).data,
    onSuccess: () => { qc.invalidateQueries(); setError(null); },
    onError: (e) => setError((e as AxiosError<{ detail?: string }>).response?.data?.detail || "Could not connect. LeetCode's endpoint is unofficial — try again or use import."),
  });

  return (
    <Page>
      <PageHeader title="LeetCode" subtitle={profile?.connected ? `Connected as ${profile.handle}` : "Connect via username (unofficial API) — behind an adapter."} />
      {!profile?.connected ? (
        <Card className="max-w-md">
          <div className="p-5">
            <label className="mb-1 block text-xs font-medium text-zinc-500">LeetCode username</label>
            <div className="flex gap-2">
              <input value={handle} onChange={(e) => setHandle(e.target.value)} placeholder="e.g. your-username"
                className="flex-1 rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-950" />
              <Button onClick={() => handle.trim() && connect.mutate(handle.trim())} disabled={connect.isPending}>
                {connect.isPending ? "Connecting…" : "Connect"}
              </Button>
            </div>
            {error && <p className="mt-2 text-sm text-red-600 dark:text-red-400">{error}</p>}
            <p className="mt-3 text-xs text-zinc-500">No official API exists; this uses the community endpoint and seeds a starter corpus so recommendations work regardless.</p>
          </div>
        </Card>
      ) : (
        <>
          <div className="mb-4 grid grid-cols-3 gap-3">
            <Metric label="Solved" value={profile.solved} />
            <Metric label="Est. level" value={profile.estimated_level ?? "—"} />
            <Metric label="In corpus" value={problems.length} />
          </div>
          <Card>
            <CardHeader title="Problems" />
            {problems.length === 0 ? <div className="p-4"><EmptyState>No problems yet.</EmptyState></div> : (
              <div className="divide-y divide-zinc-100 dark:divide-zinc-800">
                {problems.slice(0, 40).map((p) => (
                  <div key={p.id} className="flex items-center gap-3 px-4 py-2 text-sm">
                    <span className="flex-1 truncate">{p.name}</span>
                    <span className={`w-16 text-xs font-medium ${DIFF[p.difficulty || ""] || "text-zinc-500"}`}>{p.difficulty}</span>
                    <a href={p.url} target="_blank" rel="noreferrer" className="text-zinc-400 hover:text-emerald-500"><ExternalLink className="h-3.5 w-3.5" /></a>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </>
      )}
    </Page>
  );
}

function Metric({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-lg border border-zinc-200 bg-white px-3 py-2 dark:border-zinc-800 dark:bg-zinc-900">
      <div className="text-xs text-zinc-500">{label}</div>
      <div className="mt-0.5 font-mono text-lg font-semibold tabular-nums">{value}</div>
    </div>
  );
}
