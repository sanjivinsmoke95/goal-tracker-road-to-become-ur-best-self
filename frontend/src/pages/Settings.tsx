import { useQuery } from "@tanstack/react-query";
import { Moon, Sun, Check, X } from "lucide-react";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { useTheme } from "@/lib/theme";
import { Page, PageHeader } from "@/components/ui/page";
import { Card, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export function SettingsPage() {
  const { user, logout } = useAuth();
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
            <Button variant="secondary" size="sm" className="mt-2" onClick={logout}>Sign out</Button>
          </div>
        </Card>

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
