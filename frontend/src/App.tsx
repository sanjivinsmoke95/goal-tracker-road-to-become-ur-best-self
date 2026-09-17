import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import {
  Swords,
  Code2,
  CalendarClock,
  BarChart3,
  GraduationCap,
  ListChecks,
  CalendarRange,
  TrendingUp,
  Terminal,
  Bot,
  Settings,
} from "lucide-react";
import { useAuth } from "@/lib/auth";
import { AppLayout } from "@/components/layout/AppLayout";
import { Login } from "@/pages/Login";
import { DashboardPage } from "@/pages/Dashboard";
import { Placeholder } from "@/pages/Placeholder";
import type { ReactNode } from "react";

function RequireAuth({ children }: { children: ReactNode }) {
  const { isAuthenticated, loading } = useAuth();
  if (loading) {
    return <div className="grid min-h-screen place-items-center text-sm text-zinc-500">Loading…</div>;
  }
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />;
}

function PublicOnly({ children }: { children: ReactNode }) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <Navigate to="/dashboard" replace /> : <>{children}</>;
}

export function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<PublicOnly><Login mode="login" /></PublicOnly>} />
        <Route path="/register" element={<PublicOnly><Login mode="register" /></PublicOnly>} />

        <Route
          element={
            <RequireAuth>
              <AppLayout />
            </RequireAuth>
          }
        >
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<DashboardPage />} />

          <Route path="/codeforces" element={<Placeholder title="Codeforces" milestone="Milestone 3" icon={Swords} description="Connect your Codeforces handle to sync your rating, contests, submissions, and solved problems into a local database." />} />
          <Route path="/codeforces/problems" element={<Placeholder title="Codeforces · Problems" milestone="Milestone 3" icon={Swords} description="A searchable, filterable local mirror of the Codeforces problem set with your solved status." />} />
          <Route path="/codeforces/submissions" element={<Placeholder title="Codeforces · Submissions" milestone="Milestone 3" icon={Swords} description="Your full submission history with verdicts, tags, ratings, and languages." />} />

          <Route path="/leetcode" element={<Placeholder title="LeetCode" milestone="Milestone 12" icon={Code2} description="LeetCode integration via a platform adapter — public profile stats and solved problems, with a manual-import fallback." />} />
          <Route path="/leetcode/problems" element={<Placeholder title="LeetCode · Problems" milestone="Milestone 12" icon={Code2} description="LeetCode problems by difficulty and tags, with your solved status." />} />

          <Route path="/problem-of-the-day" element={<Placeholder title="Problem of the Day" milestone="Milestone 5" icon={CalendarClock} description="One Codeforces and one LeetCode problem each day, chosen by a deterministic candidate-scoring engine at your current level — with an explanation of why." />} />
          <Route path="/skills" element={<Placeholder title="Skill Analysis" milestone="Milestone 4" icon={BarChart3} description="A skill matrix built from difficulty, success rate, attempts, and recency — with Strong / Developing / Needs-reinforcement / Insufficient-data states." />} />

          <Route path="/learning" element={<Placeholder title="Learning" milestone="Milestone 8" icon={GraduationCap} description="Structured frontend, backend, and CS-fundamentals paths with theory, examples, interactive code, and official documentation." />} />
          <Route path="/learning/react" element={<Placeholder title="Learning · React" milestone="Milestone 8" icon={GraduationCap} description="The React curriculum, from JSX to project architecture." />} />
          <Route path="/learning/backend" element={<Placeholder title="Learning · Backend" milestone="Milestone 8" icon={GraduationCap} description="The backend curriculum, from HTTP to system-design fundamentals." />} />

          <Route path="/goals" element={<Placeholder title="Daily Goals" milestone="Milestone 2" icon={ListChecks} description="Your daily goal tracker with completion, streaks, and quick, professional animations." />} />
          <Route path="/plans" element={<Placeholder title="Learning Plans" milestone="Milestone 10–11" icon={CalendarRange} description="Upload a schedule (CSV / Excel / JSON) or generate an AI plan, then have it adapt to your real progress." />} />
          <Route path="/progress" element={<Placeholder title="Progress" milestone="Milestone 4+" icon={TrendingUp} description="Daily, weekly, and monthly progress charts drawn from your actual stored activity." />} />
          <Route path="/playground" element={<Placeholder title="Code Playground" milestone="Milestone 9" icon={Terminal} description="An isolated, resource-limited sandbox for JS / TS / Python / C++ — code never runs inside the API process." />} />
          <Route path="/tutor" element={<Placeholder title="AI Tutor" milestone="Milestone 6+" icon={Bot} description="A tutor that knows your skill profile and mistakes, and teaches with progressive hints rather than instant solutions." />} />
          <Route path="/settings" element={<Placeholder title="Settings" milestone="Milestone 1+" icon={Settings} description="Account, connected platforms, theme, and AI-provider configuration." />} />
        </Route>

        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
