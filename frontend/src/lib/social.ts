import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "./api";

export interface Preferences {
  display_name: string;
  daily_hours: number;
  daily_problems: number;
  target_cf_rating: number | null;
  target_lc_solved: number | null;
  desired_difficulty: "weakness" | "current" | "challenge" | "balanced";
  technologies: string[];
  goals: string;
  allow_comparison: boolean;
}

export interface Friend { id: string; email: string; full_name: string }
export interface FriendRequest { id: string; requester_id: string; addressee_id: string; status: string }
export interface Pending { incoming: FriendRequest[]; outgoing: FriendRequest[] }

export interface Metrics {
  cf_rating: number | null;
  cf_solved: number;
  lc_solved: number;
  lc_level: string | null;
  topics: Record<string, { score: number; attempts: number; solved: number; band: string }>;
  learning: { overall_pct: number; paths: Record<string, number> };
  planner: { completion_rate: number; streak: number };
  display_name?: string;
}
export interface GrowthArea { topic: string; you: number; friend: number; gap: number }
export interface ReportItem { topic: string; your_success: number; friend_success: number; suggested_action: string }
export interface Comparison {
  you: Metrics;
  friend: Metrics;
  topic_comparison: { topic: string; you: number; friend: number }[];
  your_strengths: string[];
  friend_strengths: string[];
  shared_strengths: string[];
  your_growth_areas: GrowthArea[];
  friend_growth_areas: GrowthArea[];
  shared_growth_areas: string[];
  report: ReportItem[];
}

// --- Preferences ----------------------------------------------------------
export function usePreferences() {
  return useQuery<Preferences>({
    queryKey: ["preferences"],
    queryFn: async () => (await api.get<Preferences>("/preferences")).data,
  });
}
export function useUpdatePreferences() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (p: Partial<Preferences>) => (await api.put<Preferences>("/preferences", p)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["preferences"] }),
  });
}

// --- Friends --------------------------------------------------------------
export function useFriends() {
  return useQuery<Friend[]>({ queryKey: ["friends"], queryFn: async () => (await api.get<Friend[]>("/friends")).data });
}
export function usePending() {
  return useQuery<Pending>({ queryKey: ["friends-pending"], queryFn: async () => (await api.get<Pending>("/friends/pending")).data });
}

function invalidateFriends(qc: ReturnType<typeof useQueryClient>) {
  qc.invalidateQueries({ queryKey: ["friends"] });
  qc.invalidateQueries({ queryKey: ["friends-pending"] });
}

export function useSendRequest() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (email: string) => (await api.post("/friends/request", { email })).data,
    onSuccess: () => invalidateFriends(qc),
  });
}
export function useRespond() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, accept }: { id: string; accept: boolean }) =>
      (await api.post(`/friends/${id}/${accept ? "accept" : "decline"}`)).data,
    onSuccess: () => invalidateFriends(qc),
  });
}
export function useRemoveFriend() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => api.delete(`/friends/${id}`),
    onSuccess: () => invalidateFriends(qc),
  });
}
export function useCompare(friendId: string | null) {
  return useQuery<Comparison>({
    queryKey: ["compare", friendId],
    enabled: !!friendId,
    queryFn: async () => (await api.get<Comparison>(`/friends/${friendId}/compare`)).data,
  });
}
