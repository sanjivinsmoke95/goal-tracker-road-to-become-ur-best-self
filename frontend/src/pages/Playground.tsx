import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import Editor from "@monaco-editor/react";
import { Play } from "lucide-react";
import { api } from "@/lib/api";
import { useTheme } from "@/lib/theme";
import { Page, PageHeader } from "@/components/ui/page";
import { Button } from "@/components/ui/button";

const LANGS = ["python", "javascript", "typescript", "cpp"] as const;
const MONACO_LANG: Record<string, string> = { python: "python", javascript: "javascript", typescript: "typescript", cpp: "cpp" };
const STARTERS: Record<string, string> = {
  python: "print('Hello from Python')\n",
  javascript: "console.log('Hello from Node')\n",
  typescript: "const msg: string = 'Hello TS'\nconsole.log(msg)\n",
  cpp: "#include <iostream>\nint main(){ std::cout << \"Hello C++\\n\"; }\n",
};

interface RunResult { stdout: string; stderr: string; exit_code: number | null; time_ms: number; timed_out: boolean; error?: string | null }

export function PlaygroundPage() {
  const { theme } = useTheme();
  const [language, setLanguage] = useState<string>("python");
  const [code, setCode] = useState<string>(STARTERS.python);
  const [stdin, setStdin] = useState("");

  const run = useMutation({
    mutationFn: async () => (await api.post<RunResult>("/code/run", { language, code, stdin })).data,
  });

  return (
    <Page className="max-w-6xl">
      <PageHeader
        title="Code Playground"
        subtitle="Runs in an isolated sandbox with time & memory limits — never inside the API process."
        action={
          <div className="flex items-center gap-2">
            <select value={language} onChange={(e) => { setLanguage(e.target.value); setCode(STARTERS[e.target.value] || ""); }}
              className="rounded-md border border-zinc-300 bg-white px-2 py-1.5 text-sm dark:border-zinc-700 dark:bg-zinc-950">
              {LANGS.map((l) => <option key={l} value={l}>{l}</option>)}
            </select>
            <Button size="sm" onClick={() => run.mutate()} disabled={run.isPending}>
              <Play className="h-4 w-4" /> {run.isPending ? "Running…" : "Run"}
            </Button>
          </div>
        }
      />
      <div className="grid gap-4 lg:grid-cols-2">
        <div className="overflow-hidden rounded-lg border border-zinc-200 dark:border-zinc-800">
          <Editor
            height="420px"
            language={MONACO_LANG[language]}
            theme={theme === "dark" ? "vs-dark" : "light"}
            value={code}
            onChange={(v) => setCode(v ?? "")}
            options={{ minimap: { enabled: false }, fontSize: 13, scrollBeyondLastLine: false }}
          />
        </div>
        <div className="flex flex-col gap-3">
          <div>
            <label className="mb-1 block text-xs font-medium text-zinc-500">stdin (optional)</label>
            <textarea value={stdin} onChange={(e) => setStdin(e.target.value)} rows={3}
              className="w-full rounded-md border border-zinc-300 bg-white px-3 py-2 font-mono text-xs outline-none focus:border-emerald-500 dark:border-zinc-700 dark:bg-zinc-950" />
          </div>
          <div className="flex-1 rounded-lg border border-zinc-200 bg-zinc-950 p-3 font-mono text-xs text-zinc-100 dark:border-zinc-800">
            {run.isPending ? <span className="text-zinc-500">Running…</span> : run.data ? (
              <div>
                {run.data.error && <div className="text-amber-400">⚠ {run.data.error}</div>}
                {run.data.stdout && <pre className="whitespace-pre-wrap text-emerald-300">{run.data.stdout}</pre>}
                {run.data.stderr && <pre className="whitespace-pre-wrap text-red-400">{run.data.stderr}</pre>}
                <div className="mt-2 text-zinc-500">exit {run.data.exit_code ?? "—"} · {run.data.time_ms} ms{run.data.timed_out ? " · TIMED OUT" : ""}</div>
              </div>
            ) : <span className="text-zinc-500">Output appears here.</span>}
          </div>
        </div>
      </div>
    </Page>
  );
}
