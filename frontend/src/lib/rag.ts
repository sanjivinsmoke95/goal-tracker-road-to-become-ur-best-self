import { useMutation, useQuery } from "@tanstack/react-query";
import { api } from "./api";

export interface RagSource {
  title: string;
  source: string;
  url: string;
  score: number;
}

export interface RagAnswer {
  answer: string;
  sources: RagSource[];
  grounded: boolean;
  llm: string;
}

export interface RagStatus {
  indexed_chunks: number;
  topics: string[];
  embedder: string | null;
}

export function useRagStatus() {
  return useQuery<RagStatus>({
    queryKey: ["rag-status"],
    queryFn: async () => (await api.get<RagStatus>("/rag/status")).data,
  });
}

export function useRagAsk() {
  return useMutation({
    mutationFn: async (payload: { question: string; topic?: string }) =>
      (await api.post<RagAnswer>("/rag/ask", payload)).data,
  });
}
