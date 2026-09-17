import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Bot, Lightbulb, Send } from "lucide-react";
import { api } from "@/lib/api";
import { Page, PageHeader } from "@/components/ui/page";
import { Card, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

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
    </Page>
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
