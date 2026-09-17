import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "./api";

export type GoalCategory = "cf" | "lc" | "react" | "backend" | "cs" | "other";
export type GoalPriority = "low" | "medium" | "high";
export type GoalStatus = "pending" | "in_progress" | "completed" | "skipped";

export interface Goal {
  id: string;
  title: string;
  description: string;
  category: GoalCategory;
  priority: GoalPriority;
  estimated_minutes: number;
  date: string;
  status: GoalStatus;
  completed_at: string | null;
  notes: string;
  linked_type: string | null;
  linked_ref: string | null;
}

export interface StreakSummary {
  streak: number;
  today_total: number;
  today_completed: number;
}

export interface NewGoal {
  title: string;
  category: GoalCategory;
  priority: GoalPriority;
  estimated_minutes: number;
}

function invalidate(qc: ReturnType<typeof useQueryClient>) {
  qc.invalidateQueries({ queryKey: ["goals"] });
  qc.invalidateQueries({ queryKey: ["streak"] });
  qc.invalidateQueries({ queryKey: ["dashboard"] });
}

export function useGoals() {
  return useQuery<Goal[]>({
    queryKey: ["goals", "today"],
    queryFn: async () => (await api.get<Goal[]>("/goals")).data,
  });
}

export function useStreak() {
  return useQuery<StreakSummary>({
    queryKey: ["streak"],
    queryFn: async () => (await api.get<StreakSummary>("/goals/streak")).data,
  });
}

export function useCreateGoal() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (g: NewGoal) => (await api.post<Goal>("/goals", g)).data,
    onSuccess: () => invalidate(qc),
  });
}

export function useToggleGoal() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => (await api.post<Goal>(`/goals/${id}/complete`)).data,
    onSuccess: () => invalidate(qc),
  });
}

export function useDeleteGoal() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => api.delete(`/goals/${id}`),
    onSuccess: () => invalidate(qc),
  });
}

export const CATEGORY_LABELS: Record<GoalCategory, string> = {
  cf: "Codeforces",
  lc: "LeetCode",
  react: "React",
  backend: "Backend",
  cs: "CS",
  other: "Other",
};

export const CATEGORY_STYLES: Record<GoalCategory, string> = {
  cf: "bg-rose-500/10 text-rose-500 border-rose-500/30",
  lc: "bg-amber-500/10 text-amber-500 border-amber-500/30",
  react: "bg-sky-500/10 text-sky-500 border-sky-500/30",
  backend: "bg-violet-500/10 text-violet-500 border-violet-500/30",
  cs: "bg-teal-500/10 text-teal-500 border-teal-500/30",
  other: "bg-zinc-500/10 text-zinc-400 border-zinc-500/30",
};
