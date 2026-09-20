import { NavLink, Outlet } from "react-router-dom";
import {
  LayoutDashboard,
  CalendarCheck,
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
  Moon,
  Sun,
} from "lucide-react";
import { useTheme } from "@/lib/theme";
import { useAuth } from "@/lib/auth";
import { cn } from "@/lib/utils";

const NAV = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/planner", label: "Daily Planner", icon: CalendarCheck },
  { to: "/codeforces", label: "Codeforces", icon: Swords },
  { to: "/leetcode", label: "LeetCode", icon: Code2 },
  { to: "/problem-of-the-day", label: "Problem of the Day", icon: CalendarClock },
  { to: "/skills", label: "Skill Analysis", icon: BarChart3 },
  { to: "/learning", label: "Learning", icon: GraduationCap },
  { to: "/goals", label: "Daily Goals", icon: ListChecks },
  { to: "/plans", label: "Learning Plans", icon: CalendarRange },
  { to: "/progress", label: "Progress", icon: TrendingUp },
  { to: "/playground", label: "Code Playground", icon: Terminal },
  { to: "/tutor", label: "AI Tutor", icon: Bot },
  { to: "/settings", label: "Settings", icon: Settings },
];

export function AppLayout() {
  const { theme, toggle } = useTheme();
  const { user } = useAuth();

  return (
    <div className="flex h-screen overflow-hidden">
      <aside className="flex w-60 flex-none flex-col border-r border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-900">
        <div className="flex items-center gap-2 px-4 py-4">
          <div className="grid h-8 w-8 place-items-center rounded-md bg-emerald-600 font-mono text-sm font-bold text-white">
            &gt;_
          </div>
          <div className="leading-tight">
            <div className="text-sm font-semibold">DevTrack AI</div>
            <div className="font-mono text-[11px] text-zinc-500">dev learning</div>
          </div>
        </div>

        <nav className="flex-1 space-y-0.5 overflow-y-auto px-2 py-2">
          {NAV.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-2.5 rounded-md px-2.5 py-2 text-sm transition-colors",
                  isActive
                    ? "bg-emerald-50 font-medium text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-400"
                    : "text-zinc-600 hover:bg-zinc-100 dark:text-zinc-400 dark:hover:bg-zinc-800",
                )
              }
            >
              <Icon className="h-4 w-4 flex-none" />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="border-t border-zinc-200 p-2 dark:border-zinc-800">
          <div className="flex items-center gap-2 px-1.5 py-1.5">
            <div className="grid h-8 w-8 flex-none place-items-center rounded-full bg-zinc-200 text-xs font-semibold text-zinc-700 dark:bg-zinc-800 dark:text-zinc-300">
              {(user?.email ?? "?").slice(0, 2).toUpperCase()}
            </div>
            <div className="min-w-0 flex-1">
              <div className="truncate text-xs font-medium">{user?.full_name || "You"}</div>
              <div className="truncate text-[11px] text-zinc-500">{user?.email}</div>
            </div>
          </div>
          <div className="mt-1 flex gap-1">
            <button
              onClick={toggle}
              className="flex flex-1 items-center justify-center gap-1.5 rounded-md px-2 py-1.5 text-xs text-zinc-600 hover:bg-zinc-100 dark:text-zinc-400 dark:hover:bg-zinc-800"
            >
              {theme === "dark" ? <Sun className="h-3.5 w-3.5" /> : <Moon className="h-3.5 w-3.5" />}
              {theme === "dark" ? "Light" : "Dark"}
            </button>
          </div>
        </div>
      </aside>

      <main className="flex-1 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  );
}
