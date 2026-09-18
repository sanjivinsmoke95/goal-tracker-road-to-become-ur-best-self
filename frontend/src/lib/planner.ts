import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "./api";
import type { Goal, GoalCategory, GoalPriority } from "./goals";

export type Frequency = "daily" | "weekdays" | "custom";

export interface Routine {
  id: string;
  title: string;
  description: string;
  category: GoalCategory;
  priority: GoalPriority;
  estimated_minutes: number;
  frequency: Frequency;
  days_of_week: number[];
  at_time: string | null;
  active: boolean;
}

export interface DayPlan {
  date: string;
  tasks: Goal[];
  total: number;
  completed: number;
  streak: number;
}

export interface NewRoutine {
  title: string;
  category: GoalCategory;
  priority: GoalPriority;
  estimated_minutes: number;
  frequency: Frequency;
  days_of_week: number[];
}

function invalidateDay(qc: ReturnType<typeof useQueryClient>) {
  qc.invalidateQueries({ queryKey: ["planner-day"] });
  qc.invalidateQueries({ queryKey: ["planner-missed"] });
  qc.invalidateQueries({ queryKey: ["streak"] });
  qc.invalidateQueries({ queryKey: ["dashboard"] });
  qc.invalidateQueries({ queryKey: ["goals"] });
}

export function useDay(date: string) {
  return useQuery<DayPlan>({
    queryKey: ["planner-day", date],
    queryFn: async () => (await api.get<DayPlan>("/planner/day", { params: { date } })).data,
  });
}

export function useMissed() {
  return useQuery<Goal[]>({
    queryKey: ["planner-missed"],
    queryFn: async () => (await api.get<{ tasks: Goal[] }>("/planner/missed")).data.tasks,
  });
}

export function useRoutines() {
  return useQuery<Routine[]>({
    queryKey: ["planner-routines"],
    queryFn: async () => (await api.get<Routine[]>("/planner/routines")).data,
  });
}

export function usePasteTasks() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: { text: string; date?: string }) =>
      (await api.post<Goal[]>("/planner/tasks/paste", payload)).data,
    onSuccess: () => invalidateDay(qc),
  });
}

export function useToggleTask() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => (await api.post<Goal>(`/goals/${id}/complete`)).data,
    onSuccess: () => invalidateDay(qc),
  });
}

export function useDeleteTask() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => api.delete(`/goals/${id}`),
    onSuccess: () => invalidateDay(qc),
  });
}

export function useMoveMissed() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => (await api.post<Goal>(`/planner/missed/${id}/move`)).data,
    onSuccess: () => invalidateDay(qc),
  });
}

export function useDismissMissed() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => (await api.post<Goal>(`/planner/missed/${id}/dismiss`)).data,
    onSuccess: () => invalidateDay(qc),
  });
}

export function useCreateRoutine() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (r: NewRoutine) => (await api.post<Routine>("/planner/routines", r)).data,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["planner-routines"] });
      invalidateDay(qc);
    },
  });
}

export function useToggleRoutine() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, active }: { id: string; active: boolean }) =>
      (await api.patch<Routine>(`/planner/routines/${id}`, { active })).data,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["planner-routines"] });
      invalidateDay(qc);
    },
  });
}

export function useDeleteRoutine() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => api.delete(`/planner/routines/${id}`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["planner-routines"] });
      invalidateDay(qc);
    },
  });
}

// --- date helpers ---------------------------------------------------------
export function isoDay(d: Date): string {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

export function addDays(iso: string, n: number): string {
  const d = new Date(iso + "T00:00:00");
  d.setDate(d.getDate() + n);
  return isoDay(d);
}

export const WEEKDAY_LABELS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
