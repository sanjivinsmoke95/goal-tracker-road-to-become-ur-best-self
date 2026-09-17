import { useState, type FormEvent, type InputHTMLAttributes } from "react";
import { Link, useNavigate } from "react-router-dom";
import { AxiosError } from "axios";
import { useAuth } from "@/lib/auth";
import { Button } from "@/components/ui/button";

export function Login({ mode = "login" }: { mode?: "login" | "register" }) {
  const { login, register } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const isRegister = mode === "register";

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      if (isRegister) await register(email, password, fullName);
      else await login(email, password);
      navigate("/dashboard");
    } catch (err) {
      const detail = (err as AxiosError<{ detail?: unknown }>).response?.data?.detail;
      const msg =
        typeof detail === "string"
          ? detail
          : Array.isArray(detail)
            ? (detail[0] as { msg?: string })?.msg ?? "Please check your input."
            : "Something went wrong. Please try again.";
      setError(msg);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="grid min-h-screen place-items-center px-4">
      <div className="w-full max-w-sm">
        <div className="mb-6 flex items-center gap-2">
          <div className="grid h-9 w-9 place-items-center rounded-md bg-emerald-600 font-mono text-sm font-bold text-white">
            &gt;_
          </div>
          <div>
            <div className="text-base font-semibold">Adaptive Learning OS</div>
            <div className="font-mono text-xs text-zinc-500">your personal engineering coach</div>
          </div>
        </div>

        <div className="rounded-lg border border-zinc-200 bg-white p-5 dark:border-zinc-800 dark:bg-zinc-900">
          <h1 className="text-lg font-semibold">{isRegister ? "Create your account" : "Sign in"}</h1>
          <p className="mt-1 text-sm text-zinc-500">
            {isRegister ? "One account. All your progress lives here." : "Welcome back."}
          </p>

          <form onSubmit={onSubmit} className="mt-4 space-y-3">
            {isRegister && (
              <Field label="Name" value={fullName} onChange={setFullName} placeholder="Your name" autoComplete="name" />
            )}
            <Field label="Email" type="email" value={email} onChange={setEmail} placeholder="you@example.com" required autoComplete="email" />
            <Field
              label="Password"
              type="password"
              value={password}
              onChange={setPassword}
              placeholder={isRegister ? "At least 8 characters" : "••••••••"}
              required
              autoComplete={isRegister ? "new-password" : "current-password"}
            />
            {error && (
              <div className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700 dark:bg-red-500/10 dark:text-red-400">
                {error}
              </div>
            )}
            <Button type="submit" disabled={busy} className="w-full">
              {busy ? "Please wait…" : isRegister ? "Create account" : "Sign in"}
            </Button>
          </form>
        </div>

        <p className="mt-4 text-center text-sm text-zinc-500">
          {isRegister ? (
            <>
              Already have an account?{" "}
              <Link to="/login" className="font-medium text-emerald-600 hover:underline">
                Sign in
              </Link>
            </>
          ) : (
            <>
              New here?{" "}
              <Link to="/register" className="font-medium text-emerald-600 hover:underline">
                Create an account
              </Link>
            </>
          )}
        </p>
      </div>
    </div>
  );
}

function Field({
  label,
  value,
  onChange,
  type = "text",
  ...rest
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  type?: string;
} & Omit<InputHTMLAttributes<HTMLInputElement>, "onChange" | "value" | "type">) {
  return (
    <label className="block">
      <span className="mb-1 block text-xs font-medium text-zinc-600 dark:text-zinc-400">{label}</span>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/30 dark:border-zinc-700 dark:bg-zinc-950"
        {...rest}
      />
    </label>
  );
}
