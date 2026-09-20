import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Bot, BookOpen, ExternalLink, Lightbulb, Send } from "lucide-react";
import { api } from "@/lib/api";
import { Page, PageHeader } from "@/components/ui/page";
import { Card, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useRagAsk, useRagStatus } from "@/lib/rag";

interface HintResponse { hints: string[]; solution: string | null }

export function TutorPage() {
  const [message, setMessage] = useState("");
  const [tagInput, setTagInput] = useState("dp, greedy");
  const [level, setLevel] = useState(1);

  const { data: insight } = useQuery<{ insight: string }>({
    queryKey: ["tutor-insight"],
    queryFn: async () => (await api.get<{ insight: string }>("/tutor/insight")).data,
  });

  const ask = useMutation({
    mutationFn: async () =>
      (await api.post<HintResponse>("/tutor/ask", { message, reveal_solution: false })).data,
  });
  const hint = useMutation({
    mutationFn: async () =>
      (await api.post<HintResponse>("/tutor/hint", { tags: tagInput.split(",").map((t) => t.trim()).filter(Boolean), level })).data,
  });

  return (
    <Page>
      <PageHeader title="AI Tutor" subtitle="Progressive hints, never instant solutions. It knows your level and mistakes." />

      <div className="mb-4 flex items-start gap-3 rounded-lg border border-violet-200 bg-violet-50 p-4 dark:border-violet-500/30 dark:bg-violet-500/10">
        <Lightbulb className="mt-0.5 h-5 w-5 flex-none text-violet-500" />
        <div>
          <div className="text-xs font-medium uppercase tracking-wide text-violet-500">Today's insight</div>
          <p className="mt-0.5 text-sm text-violet-800 dark:text-violet-200">{insight?.insight ?? "…"}</p>
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader title={<span className="flex items-center gap-2"><Bot className="h-4 w-4" /> Ask a question</span>} />
          <div className="p-4">
            <div className="flex gap-2">
              <input value={message} onChange={(e) => setMessage(e.target.value)} placeholder="I'm stuck on a graph problem…"
                onKeyDown={(e) => e.key === "Enter" && message.trim() && ask.mutate()}
                className="flex-1 rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-950" />
              <Button onClick={() => message.trim() && ask.mutate()} disabled={ask.isPending}><Send className="h-4 w-4" /></Button>
            </div>
            {ask.data && <HintList hints={ask.data.hints} />}
          </div>
        </Card>

        <Card>
          <CardHeader title="Topic hints" />
          <div className="p-4">
            <input value={tagInput} onChange={(e) => setTagInput(e.target.value)} placeholder="tags, comma-separated"
              className="w-full rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-950" />
            <div className="mt-2 flex items-center gap-2">
              <span className="text-xs text-zinc-500">Reveal</span>
              {[1, 2, 3].map((n) => (
                <button key={n} onClick={() => setLevel(n)}
                  className={`h-7 w-7 rounded-md text-xs ${level === n ? "bg-emerald-600 text-white" : "border border-zinc-300 dark:border-zinc-700"}`}>{n}</button>
              ))}
              <Button size="sm" className="ml-auto" onClick={() => hint.mutate()} disabled={hint.isPending}>Get hints</Button>
            </div>
            {hint.data && <HintList hints={hint.data.hints} />}
          </div>
        </Card>
      </div>

      <DocsQA />
    </Page>
  );
}

const RAG_TOPICS = ["", "dsa", "javascript", "react", "typescript", "python", "fastapi", "sql", "git"];

function DocsQA() {
  const [q, setQ] = useState("");
  const [topic, setTopic] = useState("");
  const { data: status } = useRagStatus();
  const ask = useRagAsk();

  function submit() {
    if (!q.trim()) return;
    ask.mutate({ question: q.trim(), topic: topic || undefined });
  }

  return (
    <Card className="mt-4">
      <CardHeader
        title={
          <span className="flex items-center gap-2">
            <BookOpen className="h-4 w-4" /> Ask the Docs
            <span className="rounded border border-sky-300 px-1.5 py-0.5 font-mono text-[10px] uppercase text-sky-600 dark:border-sky-500/40 dark:text-sky-400">
              RAG
            </span>
          </span>
        }
      />
      <div className="p-4">
        <p className="mb-3 text-xs text-zinc-500">
          Grounded in official documentation (React, MDN, Python, FastAPI, PostgreSQL, Git, cp-algorithms).
          Answers cite their sources.
          {status && (
            <>
              {" "}
              <span className="font-mono">{status.indexed_chunks} chunks</span> · embedder{" "}
              <span className="font-mono">{status.embedder ?? "—"}</span>
            </>
          )}
        </p>
        <div className="flex flex-wrap gap-2">
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && submit()}
            placeholder="Why is my solution O(n²)? How does useEffect cleanup work?"
            className="min-w-[200px] flex-1 rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-950"
          />
          <select
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            className="rounded-md border border-zinc-300 bg-white px-2 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-950"
          >
            {RAG_TOPICS.map((t) => (
              <option key={t} value={t}>
                {t === "" ? "All topics" : t}
              </option>
            ))}
          </select>
          <Button onClick={submit} disabled={ask.isPending || !q.trim()}>
            <Send className="h-4 w-4" /> Ask
          </Button>
        </div>

        {ask.isError && (
          <p className="mt-3 text-sm text-red-500">Couldn't reach the docs service. Is the backend running?</p>
        )}
        {ask.data && (
          <div className="mt-4">
            <div className="mb-2 flex items-center gap-2 text-[11px]">
              <span
                className={`rounded border px-1.5 py-0.5 font-mono uppercase ${
                  ask.data.llm === "retrieval-only"
                    ? "border-zinc-300 text-zinc-500 dark:border-zinc-700"
                    : "border-emerald-300 text-emerald-600 dark:border-emerald-500/40 dark:text-emerald-400"
                }`}
              >
                {ask.data.llm}
              </span>
              {ask.data.grounded && <span className="text-zinc-400">grounded in {ask.data.sources.length} source(s)</span>}
            </div>
            <div className="whitespace-pre-wrap rounded-md bg-zinc-100 px-3 py-2.5 text-sm leading-relaxed dark:bg-zinc-800">
              {ask.data.answer}
            </div>
            {ask.data.sources.length > 0 && (
              <div className="mt-3">
                <div className="mb-1.5 text-xs font-medium text-zinc-500">Sources</div>
                <div className="space-y-1">
                  {ask.data.sources.map((s, i) => (
                    <a
                      key={i}
                      href={s.url}
                      target="_blank"
                      rel="noreferrer"
                      className="flex items-center gap-2 rounded-md border border-zinc-200 px-2.5 py-1.5 text-sm hover:border-emerald-400 hover:bg-emerald-50 dark:border-zinc-800 dark:hover:bg-emerald-500/10"
                    >
                      <ExternalLink className="h-3.5 w-3.5 flex-none text-zinc-400" />
                      <span className="flex-1 truncate">{s.title}</span>
                      <span className="font-mono text-[11px] text-zinc-400">{s.source}</span>
                    </a>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </Card>
  );
}

function HintList({ hints }: { hints: string[] }) {
  return (
    <div className="mt-3 space-y-2">
      {hints.map((h, i) => (
        <div key={i} className="rounded-md bg-zinc-100 px-3 py-2 text-sm dark:bg-zinc-800">
          <span className="mr-1.5 font-mono text-xs text-emerald-600">Hint {i + 1}</span> {h}
        </div>
      ))}
    </div>
  );
}
