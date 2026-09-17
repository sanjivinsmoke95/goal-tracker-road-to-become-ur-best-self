import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Editor from "@monaco-editor/react";
import { ArrowLeft, BookOpen, Check, ExternalLink, Play } from "lucide-react";
import { api } from "@/lib/api";
import { useTheme } from "@/lib/theme";
import { Page } from "@/components/ui/page";
import { Button } from "@/components/ui/button";

interface Topic {
  id: string; title: string; theory: string; example: string; exercise: string;
  docs: { title: string; url: string; source: string }[];
  path: string; completed: boolean;
}

export function TopicDetailPage() {
  const { topicId = "" } = useParams();
  const qc = useQueryClient();
  const { theme } = useTheme();
  const { data: topic } = useQuery<Topic>({
    queryKey: ["topic", topicId],
    queryFn: async () => (await api.get<Topic>(`/learning/topics/${topicId}`)).data,
  });
  const [code, setCode] = useState("");
  const [output, setOutput] = useState<string | null>(null);
  useEffect(() => { if (topic) setCode(topic.example); }, [topic?.id]);

  const isJs = topic?.path === "react"; // frontend topics run as JS
  const run = useMutation({
    mutationFn: async () => (await api.post("/code/run", { language: isJs ? "javascript" : "python", code })).data,
    onSuccess: (r: { stdout: string; stderr: string; error?: string | null }) =>
      setOutput(r.error ? `⚠ ${r.error}` : (r.stdout || r.stderr || "(no output)")),
  });
  const complete = useMutation({
    mutationFn: async () => (await api.post(`/learning/topics/${topicId}/complete`)).data,
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["topic", topicId] }); qc.invalidateQueries({ queryKey: ["learning-paths"] }); },
  });

  if (!topic) return <Page><div className="h-60 animate-pulse rounded-lg bg-zinc-100 dark:bg-zinc-800" /></Page>;

  return (
    <Page className="max-w-6xl">
      <Link to="/learning" className="mb-4 inline-flex items-center gap-1.5 text-sm text-zinc-500 hover:text-emerald-600">
        <ArrowLeft className="h-4 w-4" /> Learning
      </Link>
      <div className="grid gap-6 lg:grid-cols-2">
        <div>
          <h1 className="text-xl font-semibold">{topic.title}</h1>
          <p className="mt-3 whitespace-pre-wrap text-sm leading-relaxed text-zinc-600 dark:text-zinc-300">{topic.theory}</p>

          <h3 className="mt-5 text-sm font-semibold">Exercise</h3>
          <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-300">{topic.exercise}</p>

          <h3 className="mt-5 flex items-center gap-1.5 text-sm font-semibold"><BookOpen className="h-4 w-4" /> Documentation</h3>
          <div className="mt-2 space-y-1.5">
            {topic.docs.map((d) => (
              <a key={d.url} href={d.url} target="_blank" rel="noreferrer"
                className="flex items-center justify-between rounded-md border border-zinc-200 px-3 py-2 text-sm hover:border-emerald-500 dark:border-zinc-800">
                <span>{d.title}</span>
                <span className="flex items-center gap-1.5 text-xs text-zinc-500">{d.source} <ExternalLink className="h-3.5 w-3.5" /></span>
              </a>
            ))}
          </div>

          <Button className="mt-5" variant={topic.completed ? "secondary" : "primary"} onClick={() => complete.mutate()} disabled={complete.isPending}>
            <Check className="h-4 w-4" /> {topic.completed ? "Completed — undo" : "Complete topic"}
          </Button>
        </div>

        <div>
          <div className="mb-2 flex items-center justify-between">
            <span className="text-sm font-medium">Playground ({isJs ? "JavaScript" : "Python"})</span>
            <Button size="sm" onClick={() => run.mutate()} disabled={run.isPending}><Play className="h-4 w-4" /> Run</Button>
          </div>
          <div className="overflow-hidden rounded-lg border border-zinc-200 dark:border-zinc-800">
            <Editor height="320px" language={isJs ? "javascript" : "python"} theme={theme === "dark" ? "vs-dark" : "light"}
              value={code} onChange={(v) => setCode(v ?? "")} options={{ minimap: { enabled: false }, fontSize: 13, scrollBeyondLastLine: false }} />
          </div>
          <div className="mt-2 min-h-[60px] rounded-lg border border-zinc-200 bg-zinc-950 p-3 font-mono text-xs text-emerald-300 dark:border-zinc-800">
            {run.isPending ? <span className="text-zinc-500">Running…</span> : <pre className="whitespace-pre-wrap">{output ?? "Output appears here."}</pre>}
          </div>
        </div>
      </div>
    </Page>
  );
}
