import { useState, type FormEvent, type ReactNode } from "react";
import { Check, UserPlus, Users, X } from "lucide-react";
import {
  useCompare,
  useFriends,
  usePending,
  useRemoveFriend,
  useRespond,
  useSendRequest,
  type Comparison,
} from "@/lib/social";
import { Page, PageHeader, EmptyState } from "@/components/ui/page";
import { Card, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export function ComparePage() {
  const { data: friends = [] } = useFriends();
  const { data: pending } = usePending();
  const send = useSendRequest();
  const respond = useRespond();
  const removeFriend = useRemoveFriend();

  const [email, setEmail] = useState("");
  const [selected, setSelected] = useState<string | null>(null);
  const { data: cmp, isLoading, isError, error } = useCompare(selected);

  function invite(e: FormEvent) {
    e.preventDefault();
    if (!email.trim()) return;
    send.mutate(email.trim(), { onSuccess: () => setEmail("") });
  }

  return (
    <Page>
      <PageHeader title="Compare" subtitle="Compare with a friend — with their consent. Neutral, no overall winner." />

      <div className="grid gap-4 lg:grid-cols-[300px_1fr]">
        {/* Left: friends + invites */}
        <div className="space-y-4">
          <Card>
            <CardHeader title={<span className="flex items-center gap-2"><UserPlus className="h-4 w-4" /> Add a friend</span>} />
            <form onSubmit={invite} className="p-4">
              <input value={email} onChange={(e) => setEmail(e.target.value)} type="email" placeholder="friend@example.com"
                className="w-full rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-950" />
              <Button type="submit" size="sm" className="mt-2 w-full" disabled={send.isPending || !email.trim()}>
                Send request
              </Button>
              {send.isError && <p className="mt-2 text-xs text-red-500">{errText(send.error)}</p>}
              {send.isSuccess && <p className="mt-2 text-xs text-emerald-600">Request sent.</p>}
            </form>
          </Card>

          {pending && pending.incoming.length > 0 && (
            <Card>
              <CardHeader title="Requests for you" />
              <div className="space-y-2 p-4">
                {pending.incoming.map((r) => (
                  <div key={r.id} className="flex items-center gap-2 text-sm">
                    <span className="flex-1 truncate font-mono text-xs text-zinc-500">{r.requester_id.slice(0, 8)}…</span>
                    <button onClick={() => respond.mutate({ id: r.id, accept: true })}
                      className="grid h-7 w-7 place-items-center rounded-md bg-emerald-600 text-white"><Check className="h-4 w-4" /></button>
                    <button onClick={() => respond.mutate({ id: r.id, accept: false })}
                      className="grid h-7 w-7 place-items-center rounded-md bg-zinc-200 dark:bg-zinc-800"><X className="h-4 w-4" /></button>
                  </div>
                ))}
              </div>
            </Card>
          )}

          <Card>
            <CardHeader title={<span className="flex items-center gap-2"><Users className="h-4 w-4" /> Friends</span>} />
            <div className="p-2">
              {friends.length === 0 ? (
                <p className="p-3 text-xs text-zinc-400">No friends yet. Send a request above.</p>
              ) : (
                friends.map((f) => (
                  <div key={f.id}
                    className={`group flex items-center gap-2 rounded-md px-2.5 py-2 text-sm ${selected === f.id ? "bg-emerald-50 dark:bg-emerald-500/10" : "hover:bg-zinc-100 dark:hover:bg-zinc-800"}`}>
                    <button onClick={() => setSelected(f.id)} className="min-w-0 flex-1 text-left">
                      <div className="truncate font-medium">{f.full_name || f.email}</div>
                      <div className="truncate text-[11px] text-zinc-400">{f.email}</div>
                    </button>
                    <button onClick={() => { removeFriend.mutate(f.id); if (selected === f.id) setSelected(null); }}
                      className="text-zinc-300 opacity-0 transition-opacity hover:text-red-500 group-hover:opacity-100" title="Remove">
                      <X className="h-4 w-4" />
                    </button>
                  </div>
                ))
              )}
            </div>
          </Card>
        </div>

        {/* Right: comparison */}
        <div>
          {!selected ? (
            <EmptyState>Select a friend to compare profiles.</EmptyState>
          ) : isLoading ? (
            <div className="h-40 animate-pulse rounded-lg bg-zinc-100 dark:bg-zinc-800" />
          ) : isError ? (
            <EmptyState>{errText(error)}</EmptyState>
          ) : cmp ? (
            <ComparisonView cmp={cmp} />
          ) : null}
        </div>
      </div>
    </Page>
  );
}

function ComparisonView({ cmp }: { cmp: Comparison }) {
  const friendName = cmp.friend.display_name || "Friend";
  return (
    <div className="space-y-4">
      {/* Headline metrics */}
      <Card>
        <CardHeader title="Profiles" />
        <div className="overflow-x-auto p-4">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs uppercase text-zinc-400">
                <th className="pb-2 font-medium">Metric</th>
                <th className="pb-2 text-right font-medium">You</th>
                <th className="pb-2 text-right font-medium">{friendName}</th>
              </tr>
            </thead>
            <tbody className="font-mono tabular-nums">
              <MetricRow label="CF rating (est.)" you={cmp.you.cf_rating ?? "—"} friend={cmp.friend.cf_rating ?? "—"} />
              <MetricRow label="CF solved" you={cmp.you.cf_solved} friend={cmp.friend.cf_solved} />
              <MetricRow label="LC solved" you={cmp.you.lc_solved} friend={cmp.friend.lc_solved} />
              <MetricRow label="Learning %" you={`${cmp.you.learning.overall_pct}%`} friend={`${cmp.friend.learning.overall_pct}%`} />
              <MetricRow label="Planner streak" you={cmp.you.planner.streak} friend={cmp.friend.planner.streak} />
            </tbody>
          </table>
        </div>
      </Card>

      {/* Strength buckets — neutral */}
      <div className="grid gap-4 sm:grid-cols-3">
        <Bucket title="Your strengths" tone="emerald" items={cmp.your_strengths} />
        <Bucket title="Shared strengths" tone="sky" items={cmp.shared_strengths} />
        <Bucket title={`${friendName}'s strengths`} tone="violet" items={cmp.friend_strengths} />
      </div>

      {/* Per-topic bars */}
      {cmp.topic_comparison.length > 0 && (
        <Card>
          <CardHeader title="Topic success rate (you vs friend)" />
          <div className="space-y-3 p-4">
            {cmp.topic_comparison.map((t) => (
              <div key={t.topic}>
                <div className="mb-1 flex justify-between text-xs">
                  <span className="capitalize">{t.topic}</span>
                  <span className="font-mono text-zinc-400">{t.you}% · {t.friend}%</span>
                </div>
                <div className="flex gap-1">
                  <div className="h-2 flex-1 overflow-hidden rounded-full bg-zinc-100 dark:bg-zinc-800">
                    <div className="h-full rounded-full bg-emerald-500" style={{ width: `${t.you}%` }} />
                  </div>
                  <div className="h-2 flex-1 overflow-hidden rounded-full bg-zinc-100 dark:bg-zinc-800">
                    <div className="h-full rounded-full bg-violet-500" style={{ width: `${t.friend}%` }} />
                  </div>
                </div>
              </div>
            ))}
            <div className="flex gap-4 text-[11px] text-zinc-400">
              <span className="flex items-center gap-1"><span className="h-2 w-2 rounded-full bg-emerald-500" /> You</span>
              <span className="flex items-center gap-1"><span className="h-2 w-2 rounded-full bg-violet-500" /> {friendName}</span>
            </div>
          </div>
        </Card>
      )}

      {/* Personalized report */}
      {cmp.report.length > 0 && (
        <Card>
          <CardHeader title="Your improvement areas" />
          <div className="space-y-3 p-4">
            {cmp.report.map((r) => (
              <div key={r.topic} className="rounded-lg border border-zinc-200 p-3 dark:border-zinc-800">
                <div className="flex items-center justify-between">
                  <span className="font-medium capitalize">{r.topic}</span>
                  <span className="font-mono text-xs text-zinc-400">you {r.your_success}% · friend {r.friend_success}%</span>
                </div>
                <p className="mt-1 text-sm text-emerald-700 dark:text-emerald-400">→ {r.suggested_action}</p>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}

function MetricRow({ label, you, friend }: { label: string; you: ReactNode; friend: ReactNode }) {
  return (
    <tr className="border-t border-zinc-100 dark:border-zinc-800">
      <td className="py-2 font-sans text-zinc-500">{label}</td>
      <td className="py-2 text-right font-semibold text-emerald-600">{you}</td>
      <td className="py-2 text-right font-semibold text-violet-600">{friend}</td>
    </tr>
  );
}

const TONE: Record<string, string> = {
  emerald: "border-emerald-300 text-emerald-700 dark:border-emerald-500/40 dark:text-emerald-400",
  sky: "border-sky-300 text-sky-700 dark:border-sky-500/40 dark:text-sky-400",
  violet: "border-violet-300 text-violet-700 dark:border-violet-500/40 dark:text-violet-400",
};
function Bucket({ title, tone, items }: { title: string; tone: string; items: string[] }) {
  return (
    <Card>
      <CardHeader title={<span className="text-sm">{title}</span>} />
      <div className="flex flex-wrap gap-1.5 p-4">
        {items.length === 0 ? (
          <span className="text-xs text-zinc-400">—</span>
        ) : (
          items.map((t) => (
            <span key={t} className={`rounded border px-2 py-0.5 text-xs capitalize ${TONE[tone]}`}>{t}</span>
          ))
        )}
      </div>
    </Card>
  );
}

function errText(e: unknown): string {
  const detail = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
  return typeof detail === "string" ? detail : "Something went wrong.";
}
