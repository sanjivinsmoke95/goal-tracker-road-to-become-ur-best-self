import { useEffect, useState, type ReactNode } from "react";
import { useQuery } from "@tanstack/react-query";
import { Moon, Sun, Check, X } from "lucide-react";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { useTheme } from "@/lib/theme";
import { usePreferences, useUpdatePreferences, type Preferences } from "@/lib/social";
import { Page, PageHeader } from "@/components/ui/page";
import { Card, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export function SettingsPage() {
  const { user } = useAuth();
  const { theme, toggle } = useTheme();
  const { data: cf } = useQuery<{ handle: string } | null>({ queryKey: ["cf-profile"], queryFn: async () => (await api.get("/codeforces/profile")).data });
  const { data: lc } = useQuery<{ connected: boolean; handle: string | null }>({ queryKey: ["lc-profile"], queryFn: async () => (await api.get("/leetcode/profile")).data });

  return (
    <Page>
      <PageHeader title="Settings" />
      <div className="space-y-4">
        <Card>
          <CardHeader title="Account" />
          <div className="space-y-2 p-4 text-sm">
            <Row label="Name" value={user?.full_name || "—"} />
            <Row label="Email" value={user?.email || "—"} />
          </div>
        </Card>

        <PersonalizationCard />

        <Card>
          <CardHeader title="Connected platforms" />
          <div className="space-y-2 p-4 text-sm">
            <Platform name="Codeforces" connected={!!cf} handle={cf?.handle} />
            <Platform name="LeetCode" connected={!!lc?.connected} handle={lc?.handle} />
          </div>
        </Card>

        <Card>
          <CardHeader title="Appearance" />
          <div className="flex items-center justify-between p-4 text-sm">
            <span>Theme</span>
            <Button variant="secondary" size="sm" onClick={toggle}>
              {theme === "dark" ? <><Sun className="h-4 w-4" /> Light</> : <><Moon className="h-4 w-4" /> Dark</>}
            </Button>
          </div>
        </Card>

        <Card>
          <CardHeader title="AI provider" />
          <div className="space-y-1 p-4 text-sm text-zinc-500">
            <p>The AI layer is provider-agnostic (default: <span className="font-mono">Gemini</span>, with a keyless stub fallback).</p>
            <p>Configure <span className="font-mono">AI_PROVIDER</span> and <span className="font-mono">GEMINI_API_KEY</span> in the backend <span className="font-mono">.env</span> to enable full AI code review, tutoring, and plan generation.</p>
          </div>
        </Card>
      </div>
    </Page>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return <div className="flex justify-between"><span className="text-zinc-500">{label}</span><span>{value}</span></div>;
}

const DIFFICULTIES: Preferences["desired_difficulty"][] = ["weakness", "current", "balanced", "challenge"];

function PersonalizationCard() {
  const { data } = usePreferences();
  const update = useUpdatePreferences();
  const [form, setForm] = useState<Partial<Preferences>>({});

  useEffect(() => { if (data) setForm(data); }, [data]);

  function set<K extends keyof Preferences>(key: K, value: Preferences[K]) {
    setForm((f) => ({ ...f, [key]: value }));
  }
  function save() {
    update.mutate({
      daily_hours: form.daily_hours,
      daily_problems: form.daily_problems,
      target_cf_rating: form.target_cf_rating,
      target_lc_solved: form.target_lc_solved,
      desired_difficulty: form.desired_difficulty,
      goals: form.goals,
      allow_comparison: form.allow_comparison,
    });
  }

  return (
    <Card>
      <CardHeader title="Personalization" />
      <div className="grid gap-3 p-4 text-sm sm:grid-cols-2">
        <Field label="Daily hours">
          <input type="number" min={0} max={24} step={0.5} value={form.daily_hours ?? 2}
            onChange={(e) => set("daily_hours", Number(e.target.value))} className={inputCls} />
        </Field>
        <Field label="Problems / day">
          <input type="number" min={0} max={50} value={form.daily_problems ?? 2}
            onChange={(e) => set("daily_problems", Number(e.target.value))} className={inputCls} />
        </Field>
        <Field label="Target CF rating">
          <input type="number" min={0} max={4000} value={form.target_cf_rating ?? ""}
            onChange={(e) => set("target_cf_rating", e.target.value ? Number(e.target.value) : null)} className={inputCls} />
        </Field>
        <Field label="Target LC solved">
          <input type="number" min={0} value={form.target_lc_solved ?? ""}
            onChange={(e) => set("target_lc_solved", e.target.value ? Number(e.target.value) : null)} className={inputCls} />
        </Field>
        <Field label="Practice focus">
          <select value={form.desired_difficulty ?? "balanced"} onChange={(e) => set("desired_difficulty", e.target.value as Preferences["desired_difficulty"])} className={inputCls}>
            {DIFFICULTIES.map((d) => <option key={d} value={d}>{d}</option>)}
          </select>
        </Field>
        <Field label="Compare with friends">
          <label className="flex items-center gap-2">
            <input type="checkbox" checked={form.allow_comparison ?? true} onChange={(e) => set("allow_comparison", e.target.checked)} />
            <span className="text-xs text-zinc-500">allow friends to compare with my profile</span>
          </label>
        </Field>
        <div className="sm:col-span-2">
          <Field label="Current goals">
            <textarea rows={2} value={form.goals ?? ""} onChange={(e) => set("goals", e.target.value)} className={inputCls} />
          </Field>
        </div>
      </div>
      <div className="flex items-center justify-end gap-2 px-4 pb-4">
        {update.isSuccess && <span className="text-xs text-emerald-600">Saved.</span>}
        <Button size="sm" onClick={save} disabled={update.isPending}>Save preferences</Button>
      </div>
    </Card>
  );
}

const inputCls = "w-full rounded-md border border-zinc-300 bg-white px-2.5 py-1.5 text-sm outline-none focus:border-emerald-500 dark:border-zinc-700 dark:bg-zinc-950";

function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <label className="block">
      <span className="mb-1 block text-xs font-medium text-zinc-500">{label}</span>
      {children}
    </label>
  );
}
function Platform({ name, connected, handle }: { name: string; connected: boolean; handle?: string | null }) {
  return (
    <div className="flex items-center justify-between">
      <span>{name}{handle ? ` · ${handle}` : ""}</span>
      <span className={`flex items-center gap-1 text-xs ${connected ? "text-emerald-600" : "text-zinc-400"}`}>
        {connected ? <><Check className="h-3.5 w-3.5" /> Connected</> : <><X className="h-3.5 w-3.5" /> Not connected</>}
      </span>
    </div>
  );
}
