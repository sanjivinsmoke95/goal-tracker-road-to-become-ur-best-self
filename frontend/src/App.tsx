import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import type { ReactNode } from "react";
import { useAuth } from "@/lib/auth";
import { AppLayout } from "@/components/layout/AppLayout";
import { DashboardPage } from "@/pages/Dashboard";
import { PlannerPage } from "@/pages/Planner";
import { GoalsPage } from "@/pages/Goals";
import { CodeforcesPage } from "@/pages/Codeforces";
import { LeetCodePage } from "@/pages/LeetCode";
import { ProblemOfTheDayPage } from "@/pages/ProblemOfTheDay";
import { SkillsPage } from "@/pages/Skills";
import { LearningPage } from "@/pages/Learning";
import { TopicDetailPage } from "@/pages/TopicDetail";
import { PlansPage } from "@/pages/Plans";
import { ProgressPage } from "@/pages/Progress";
import { PlaygroundPage } from "@/pages/Playground";
import { TutorPage } from "@/pages/Tutor";
import { SettingsPage } from "@/pages/Settings";

// Single-user app: there is no login. We just wait for the silent local sign-in
// (see AuthProvider) before rendering the app shell.
function RequireAuth({ children }: { children: ReactNode }) {
  const { isAuthenticated, loading, error } = useAuth();
  if (error)
    return (
      <div className="grid min-h-screen place-items-center px-6 text-center text-sm text-red-600">{error}</div>
    );
  if (loading || !isAuthenticated)
    return <div className="grid min-h-screen place-items-center text-sm text-zinc-500">Loading…</div>;
  return <>{children}</>;
}

export function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<RequireAuth><AppLayout /></RequireAuth>}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/planner" element={<PlannerPage />} />
          <Route path="/codeforces" element={<CodeforcesPage />} />
          <Route path="/codeforces/problems" element={<CodeforcesPage />} />
          <Route path="/codeforces/submissions" element={<CodeforcesPage />} />
          <Route path="/leetcode" element={<LeetCodePage />} />
          <Route path="/leetcode/problems" element={<LeetCodePage />} />
          <Route path="/problem-of-the-day" element={<ProblemOfTheDayPage />} />
          <Route path="/skills" element={<SkillsPage />} />
          <Route path="/learning" element={<LearningPage />} />
          <Route path="/learning/react" element={<LearningPage />} />
          <Route path="/learning/backend" element={<LearningPage />} />
          <Route path="/learning/topic/:topicId" element={<TopicDetailPage />} />
          <Route path="/goals" element={<GoalsPage />} />
          <Route path="/plans" element={<PlansPage />} />
          <Route path="/progress" element={<ProgressPage />} />
          <Route path="/playground" element={<PlaygroundPage />} />
          <Route path="/tutor" element={<TutorPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Route>

        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
