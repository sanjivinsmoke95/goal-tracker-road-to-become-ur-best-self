import { createContext, useContext, useEffect, useRef, useState, type ReactNode } from "react";
import { useQuery } from "@tanstack/react-query";
import { api, getToken, setToken } from "./api";

export interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  created_at: string;
}

interface AuthValue {
  user: User | null;
  loading: boolean;
  isAuthenticated: boolean;
  error: string | null;
}

const AuthContext = createContext<AuthValue>(null as unknown as AuthValue);

// This is a single-user personal app, so there is no login page. On startup we
// silently sign in to one fixed local account (creating it the first time), and
// every screen just works. The credentials are a local convenience, not a
// security boundary — the app is meant to run on the owner's own machine.
const OWNER = {
  email: "owner@example.com",
  password: "learnos-local-owner",
  full_name: "Owner",
};

async function bootstrapToken(): Promise<string> {
  const loginOwner = async () => {
    const { data } = await api.post<{ access_token: string }>("/auth/login", {
      email: OWNER.email,
      password: OWNER.password,
    });
    return data.access_token;
  };
  try {
    return await loginOwner();
  } catch {
    // First run (or wiped DB): create the local account, then sign in.
    await api.post("/auth/register", OWNER).catch(() => {});
    return await loginOwner();
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setTok] = useState<string | null>(getToken());
  const [error, setError] = useState<string | null>(null);
  const bootstrapping = useRef(false);

  useEffect(() => {
    if (token || bootstrapping.current) return;
    bootstrapping.current = true;
    bootstrapToken()
      .then((t) => {
        setToken(t);
        setTok(t);
      })
      .catch(() => setError("Could not reach the backend. Is it running?"))
      .finally(() => {
        bootstrapping.current = false;
      });
  }, [token]);

  const { data: user, isLoading } = useQuery<User | null>({
    queryKey: ["me", token],
    enabled: !!token,
    queryFn: async () => {
      try {
        const { data } = await api.get<User>("/auth/me");
        return data;
      } catch {
        // A stale token (e.g. DB was reset) — drop it and re-bootstrap.
        setToken(null);
        setTok(null);
        return null;
      }
    },
    retry: false,
  });

  return (
    <AuthContext.Provider
      value={{
        user: user ?? null,
        loading: (!token || isLoading) && !error,
        isAuthenticated: !!token && !!user,
        error,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
