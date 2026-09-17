import { useQuery } from "@tanstack/react-query";
import { AnimatePresence, motion } from "framer-motion";
import { Link } from "react-router-dom";
import { Flame, Swords, Code2, Link2, Database, Lightbulb, Sparkles, Plus } from "lucide-react";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { Card, CardHeader } from "@/components/ui/card";
import { GoalRow } from "@/components/GoalRow";
import { useGoals, useToggleGoal } from "@/lib/goals";

interface PlatformStatus {
  connected: boolean;
  handle: string | null;
  detail: string;
}
interface SkillSnapshot {
  available: boolean;
  estimated_cf_rating: number | null;
  estimated_lc_level: string | null;
  strong_topics: string[];
  reinforce_topics: string[];
  note: string;
}
interface Dashboard {
  streak: number;
  platforms: Record<string, PlatformStatus>;
  problem_of_the_day: Record<string, unknown | null>;
  today_goals: unknown[];
  skill_snapshot: SkillSnapshot;
  provenance: Record<string, string>;
}

export function DashboardPage() {
  const { user } = useAuth();
  const { data, isLoading, isError } = useQuery<Dashboard>({
    queryKey: ["dashboard"],
    queryFn: async () => (await api.get<Dashboard>("/dashboard")).data,
  });

  const firstName = (user?.full_name || user?.email || "there").split(/[@ ]/)[0];

  return (
    <div className="mx-auto max-w-5xl px-6 py-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-semibold">Good to see you, {firstName}.</h1>
          <p className="text-sm text-zinc-500">Here's what today looks like.</p>
        </div>
        <StreakBadge streak={data?.streak ?? 0} loading={isLoading} />
      </div>

      {isError && (
        <div className="mt-4 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700 dark:bg-red-500/10 dark:text-red-400">
          Couldn't load your dashboard. Is the backend running on {import.meta.env.VITE_API_URL || "http://localhost:8000"}?
        </div>
      )}

      <Insight />

      <motion.div
        initial={{ opacity: 0, y: 6 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.25 }}
        className="mt-6 grid gap-4 lg:grid-cols-2"
      >
        <DashboardPotd label="Codeforces" icon={Swords} platform="codeforces" connected={data?.platforms.codeforces?.connected} loading={isLoading} />
        <DashboardPotd label="LeetCode" icon={Code2} platform="leetcode" connected={data?.platforms.leetcode?.connected} loading={isLoading} />
      </motion.div>

      <div className="mt-4 grid gap-4 lg:grid-cols-2">
        <TodaysLearning />

        <Card>
          <CardHeader title="Skill Snapshot" action={<InferenceTag />} />
          <div className="px-4 py-4">
            {data?.skill_snapshot.available ? null : (
              <p className="text-sm text-zinc-500">{data?.skill_snapshot.note ?? "Loading…"}</p>
            )}
            <div className="mt-3 grid grid-cols-2 gap-3 text-sm">
              <Metric label="Est. CF level" value={data?.skill_snapshot.estimated_cf_rating ?? "—"} />
              <Metric label="Est. LC level" value={data?.skill_snapshot.estimated_lc_level ?? "—"} />
            </div>
            {data?.skill_snapshot.available && (
              <div className="mt-3 space-y-1.5 text-xs">
                {data.skill_snapshot.strong_topics.length > 0 && (
                  <div><span className="text-emerald-600">Strong:</span> {data.skill_snapshot.strong_topics.join(", ")}</div>
                )}
                {data.skill_snapshot.reinforce_topics.length > 0 && (
                  <div><span className="text-amber-600">Reinforce:</span> {data.skill_snapshot.reinforce_topics.join(", ")}</div>
                )}
              </div>
            )}
          </div>
        </Card>
      </div>

      {data?.provenance && <Provenance provenance={data.provenance} />}
    </div>
  );
}

function TodaysLearning() {
  const { data: goals = [], isLoading } = useGoals();
  const toggle = useToggleGoal();
  const done = goals.filter((g) => g.status === "completed").length;

  return (
    <Card>
      <CardHeader
        title="Today's Learning"
        action={
          <span className="font-mono text-xs text-zinc-500">
            {isLoading ? "…" : `${done}/${goals.length}`}
          </span>
        }
      />
      <div className="space-y-1.5 p-3">
        {isLoading ? (
          <div className="h-10 animate-pulse rounded-md bg-zinc-100 dark:bg-zinc-800" />
        ) : goals.length === 0 ? (
          <Link
            to="/goals"
            className="flex items-center justify-center gap-1.5 rounded-md border border-dashed border-zinc-300 py-6 text-sm text-zinc-500 hover:border-emerald-500 hover:text-emerald-600 dark:border-zinc-700"
          >
            <Plus className="h-4 w-4" /> Add today's goals
          </Link>
        ) : (
          <AnimatePresence initial={false}>
            {goals.map((g) => (
              <GoalRow key={g.id} goal={g} onToggle={(id) => toggle.mutate(id)} busy={toggle.isPending} />
            ))}
          </AnimatePresence>
        )}
      </div>
    </Card>
  );
}

function StreakBadge({ streak, loading }: { streak: number; loading: boolean }) {
  return (
    <div className="inline-flex items-center gap-2 rounded-full border border-orange-200 bg-orange-50 px-3 py-1.5 text-sm font-semibold text-orange-700 dark:border-orange-500/30 dark:bg-orange-500/10 dark:text-orange-400">
      <Flame className="h-4 w-4" />
      {loading ? "…" : `${streak} day streak`}
    </div>
  );
}

interface DailyMini {
  problem: { name: string; rating: number | null; difficulty: string | null; tags: string[]; url: string } | null;
  explanation: string;
}

function Insight() {
  const { data } = useQuery<{ insight: string }>({
    queryKey: ["tutor-insight"],
    queryFn: async () => (await api.get<{ insight: string }>("/tutor/insight")).data,
  });
  if (!data?.insight) return null;
  return (
    <div className="mt-4 flex items-start gap-2.5 rounded-lg border border-violet-200 bg-violet-50 px-3 py-2.5 text-sm dark:border-violet-500/30 dark:bg-violet-500/10">
      <Sparkles className="mt-0.5 h-4 w-4 flex-none text-violet-500" />
      <span className="text-violet-800 dark:text-violet-200">{data.insight}</span>
    </div>
  );
}

function DashboardPotd({ label, icon: Icon, platform, connected, loading }: { label: string; icon: typeof Swords; platform: string; connected?: boolean; loading: boolean }) {
  const { data } = useQuery<{ codeforces: DailyMini | null; leetcode: DailyMini | null }>({
    queryKey: ["potd"],
    queryFn: async () => (await api.get("/problems/today")).data,
    enabled: !!connected,
  });
  const daily = platform === "codeforces" ? data?.codeforces : data?.leetcode;

  return (
    <Card>
      <CardHeader title={`${label} · Problem of the Day`} action={<RecommendationTag />} />
      <div className="px-4 py-5">
        {loading ? (
          <div className="h-16 animate-pulse rounded-md bg-zinc-100 dark:bg-zinc-800" />
        ) : !connected ? (
          <div className="flex items-start gap-3">
            <Icon className="mt-0.5 h-5 w-5 flex-none text-zinc-400" />
            <div>
              <p className="text-sm font-medium">Connect your {label} account</p>
              <p className="mt-0.5 text-sm text-zinc-500">Your Problem of the Day comes from your real solving history.</p>
              <Link to={`/${platform}`} className="mt-2 inline-flex items-center gap-1.5 text-sm font-medium text-emerald-600 hover:underline">
                <Link2 className="h-3.5 w-3.5" /> Connect
              </Link>
            </div>
          </div>
        ) : !daily?.problem ? (
          <p className="text-sm text-zinc-500">No recommendation yet — sync your account.</p>
        ) : (
          <div>
            <div className="flex items-start justify-between gap-2">
              <div className="text-sm font-semibold">{daily.problem.name}</div>
              <a href={daily.problem.url} target="_blank" rel="noreferrer" className="shrink-0 text-xs font-medium text-emerald-600 hover:underline">Solve →</a>
            </div>
            <div className="mt-1 flex flex-wrap gap-1.5 text-[11px] text-zinc-500">
              {daily.problem.rating != null && <span className="rounded bg-zinc-100 px-1.5 py-0.5 font-mono dark:bg-zinc-800">{daily.problem.rating}</span>}
              {daily.problem.difficulty && <span className="rounded bg-zinc-100 px-1.5 py-0.5 dark:bg-zinc-800">{daily.problem.difficulty}</span>}
              {daily.problem.tags.slice(0, 3).map((t) => <span key={t} className="rounded bg-zinc-100 px-1.5 py-0.5 dark:bg-zinc-800">{t}</span>)}
            </div>
            <p className="mt-2 line-clamp-2 text-xs text-zinc-500">{daily.explanation}</p>
          </div>
        )}
      </div>
    </Card>
  );
}

function Metric({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-md border border-zinc-200 px-3 py-2 dark:border-zinc-800">
      <div className="text-xs text-zinc-500">{label}</div>
      <div className="mt-0.5 font-mono text-lg font-semibold tabular-nums">{value}</div>
    </div>
  );
}

function Provenance({ provenance }: { provenance: Record<string, string> }) {
  const items = [
    { key: "data", icon: Database, label: "Data", tone: "text-sky-600 dark:text-sky-400" },
    { key: "inference", icon: Sparkles, label: "Inference", tone: "text-violet-600 dark:text-violet-400" },
    { key: "recommendation", icon: Lightbulb, label: "Recommendation", tone: "text-emerald-600 dark:text-emerald-400" },
  ];
  return (
    <div className="mt-6 rounded-lg border border-dashed border-zinc-300 bg-white/50 px-4 py-3 dark:border-zinc-700 dark:bg-zinc-900/40">
      <div className="mb-2 text-xs font-medium uppercase tracking-wide text-zinc-500">How to read this app</div>
      <div className="grid gap-3 sm:grid-cols-3">
        {items.map(({ key, icon: Icon, label, tone }) => (
          <div key={key} className="flex items-start gap-2">
            <Icon className={`mt-0.5 h-4 w-4 flex-none ${tone}`} />
            <div>
              <div className={`text-xs font-semibold ${tone}`}>{label}</div>
              <div className="text-xs text-zinc-500">{provenance[key]}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

const InferenceTag = () => (
  <span className="rounded border border-violet-300 px-1.5 py-0.5 font-mono text-[10px] uppercase text-violet-600 dark:border-violet-500/40 dark:text-violet-400">
    inference
  </span>
);
const RecommendationTag = () => (
  <span className="rounded border border-emerald-300 px-1.5 py-0.5 font-mono text-[10px] uppercase text-emerald-600 dark:border-emerald-500/40 dark:text-emerald-400">
    recommendation
  </span>
);
