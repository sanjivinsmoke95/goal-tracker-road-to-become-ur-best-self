import { createContext, useContext, useState, type ReactNode } from "react";
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
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthValue>(null as unknown as AuthValue);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setTok] = useState<string | null>(getToken());

  const { data: user, isLoading } = useQuery<User | null>({
    queryKey: ["me", token],
    enabled: !!token,
    queryFn: async () => {
      const { data } = await api.get<User>("/auth/me");
      return data;
    },
    retry: false,
  });

  async function login(email: string, password: string) {
    const { data } = await api.post<{ access_token: string }>("/auth/login", { email, password });
    setToken(data.access_token);
    setTok(data.access_token);
  }

  async function register(email: string, password: string, fullName: string) {
    await api.post("/auth/register", { email, password, full_name: fullName });
    await login(email, password);
  }

  function logout() {
    setToken(null);
    setTok(null);
  }

  return (
    <AuthContext.Provider
      value={{
        user: user ?? null,
        loading: !!token && isLoading,
        isAuthenticated: !!token && !!user,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
