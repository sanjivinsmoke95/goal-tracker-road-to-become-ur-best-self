import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import Editor from "@monaco-editor/react";
import { ExternalLink, Gauge, Play, ScanSearch } from "lucide-react";
import { api } from "@/lib/api";
import { useTheme } from "@/lib/theme";
import { Page, PageHeader } from "@/components/ui/page";
import { Card, CardHeader } from "@/components/ui/card";
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

      <AnalyzePanel code={code} language={language} />
    </Page>
  );
}

interface Complexity {
  time: string;
  space: string;
  reason: string;
  loop_nesting: number;
  uses_sort: boolean;
  uses_recursion: boolean;
  estimate: boolean;
}
interface Finding { type: string; severity: string; note: string }
interface Review {
  correctness: string;
  strengths: string[];
  improvements: string[];
  summary: string;
}
interface AnalyzeResult {
  complexity: Complexity;
  findings: Finding[];
  review: Review;
  answer: string | null;
  sources: { title: string; source: string; url: string; score: number }[];
  llm: string;
}

const SEV_STYLE: Record<string, string> = {
  high: "border-red-400/40 bg-red-500/10 text-red-500",
  medium: "border-amber-400/40 bg-amber-500/10 text-amber-500",
  low: "border-zinc-400/40 bg-zinc-500/10 text-zinc-400",
};

function AnalyzePanel({ code, language }: { code: string; language: string }) {
  const [constraints, setConstraints] = useState("");
  const [verdict, setVerdict] = useState("");
  const [question, setQuestion] = useState("");

  const analyze = useMutation({
    mutationFn: async () =>
      (await api.post<AnalyzeResult>("/code/analyze", { language, code, constraints, verdict, question })).data,
  });
  const r = analyze.data;

  return (
    <Card className="mt-4">
      <CardHeader
        title={
          <span className="flex items-center gap-2">
            <ScanSearch className="h-4 w-4" /> Analyze this code
            <span className="rounded border border-violet-300 px-1.5 py-0.5 font-mono text-[10px] uppercase text-violet-600 dark:border-violet-500/40 dark:text-violet-400">
              static + AI
            </span>
          </span>
        }
      />
      <div className="p-4">
        <div className="grid gap-2 sm:grid-cols-3">
          <input value={constraints} onChange={(e) => setConstraints(e.target.value)} placeholder="Constraints e.g. n ≤ 10^5"
            className="rounded-md border border-zinc-300 bg-white px-2.5 py-1.5 text-sm dark:border-zinc-700 dark:bg-zinc-950" />
          <input value={verdict} onChange={(e) => setVerdict(e.target.value)} placeholder="Verdict e.g. TLE / WA / OK"
            className="rounded-md border border-zinc-300 bg-white px-2.5 py-1.5 text-sm dark:border-zinc-700 dark:bg-zinc-950" />
          <input value={question} onChange={(e) => setQuestion(e.target.value)} placeholder="Ask: why is this slow?"
            className="rounded-md border border-zinc-300 bg-white px-2.5 py-1.5 text-sm dark:border-zinc-700 dark:bg-zinc-950" />
        </div>
        <div className="mt-2 flex justify-end">
          <Button size="sm" onClick={() => analyze.mutate()} disabled={analyze.isPending || !code.trim()}>
            <Gauge className="h-4 w-4" /> {analyze.isPending ? "Analyzing…" : "Analyze"}
          </Button>
        </div>

        {r && (
          <div className="mt-4 space-y-4">
            {/* Complexity — heuristic estimate */}
            <div className="rounded-lg border border-zinc-200 p-3 dark:border-zinc-800">
              <div className="mb-1 flex items-center gap-2 text-xs font-medium text-zinc-500">
                Estimated complexity
                <span className="rounded border border-violet-300 px-1 py-0.5 font-mono text-[10px] uppercase text-violet-500 dark:border-violet-500/40">
                  inference
                </span>
              </div>
              <div className="flex flex-wrap gap-4 text-sm">
                <span>Time <span className="font-mono font-semibold text-emerald-600">{r.complexity.time}</span></span>
                <span>Space <span className="font-mono font-semibold text-emerald-600">{r.complexity.space}</span></span>
              </div>
              <p className="mt-1 text-xs text-zinc-500">{r.complexity.reason}</p>
            </div>

            {/* Findings */}
            {r.findings.length > 0 && (
              <div>
                <div className="mb-1.5 text-xs font-medium text-zinc-500">Findings</div>
                <div className="space-y-1.5">
                  {r.findings.map((f, i) => (
                    <div key={i} className="flex items-start gap-2 rounded-md border border-zinc-200 px-2.5 py-2 text-sm dark:border-zinc-800">
                      <span className={`rounded border px-1.5 py-0.5 text-[10px] font-medium uppercase ${SEV_STYLE[f.severity] ?? SEV_STYLE.low}`}>
                        {f.severity}
                      </span>
                      <span className="flex-1">{f.note}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* AI review summary */}
            {r.review?.summary && (
              <div className="rounded-lg bg-zinc-100 px-3 py-2.5 text-sm dark:bg-zinc-800">
                <div className="mb-1 text-xs font-medium text-zinc-500">Review — correctness: {r.review.correctness}</div>
                {r.review.improvements?.length > 0 && (
                  <ul className="ml-4 list-disc space-y-0.5">
                    {r.review.improvements.map((s, i) => <li key={i}>{s}</li>)}
                  </ul>
                )}
                <p className="mt-1 text-xs text-zinc-500">{r.review.summary}</p>
              </div>
            )}

            {/* Grounded answer to the question */}
            {r.answer && (
              <div>
                <div className="mb-1 flex items-center gap-2 text-xs font-medium text-zinc-500">
                  Answer
                  <span className="rounded border border-zinc-300 px-1 py-0.5 font-mono text-[10px] uppercase text-zinc-500 dark:border-zinc-700">
                    {r.llm}
                  </span>
                </div>
                <div className="whitespace-pre-wrap rounded-md bg-zinc-100 px-3 py-2.5 text-sm dark:bg-zinc-800">{r.answer}</div>
                {r.sources.length > 0 && (
                  <div className="mt-2 space-y-1">
                    {r.sources.map((s, i) => (
                      <a key={i} href={s.url} target="_blank" rel="noreferrer"
                        className="flex items-center gap-2 rounded-md border border-zinc-200 px-2.5 py-1.5 text-sm hover:border-emerald-400 dark:border-zinc-800">
                        <ExternalLink className="h-3.5 w-3.5 flex-none text-zinc-400" />
                        <span className="flex-1 truncate">{s.title}</span>
                        <span className="font-mono text-[11px] text-zinc-400">{s.source}</span>
                      </a>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </Card>
  );
}
