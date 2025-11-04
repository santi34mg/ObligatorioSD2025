import {
  createContext,
  useContext,
  useState,
  useEffect,
  type ReactNode,
} from "react";
import { type UserRole } from "@/lib/roles";

interface User {
  id: string;
  email: string;
  role: UserRole;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  login: (token: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
  isAdmin: () => boolean;
  isStudent: () => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem("access_token");
    if (token) {
      fetchUser(token);
    } else {
      setIsLoading(false);
    }
  }, []);

  const fetchUser = async (token: string) => {
    try {
      console.log("Fetching user with token:", token.substring(0, 20) + "...");

      // fastapi-users provides /users/me endpoint through get_users_router
      const response = await fetch("http://localhost/api/users/me", {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      console.log("Fetch user response status:", response.status);

      if (response.ok) {
        const userData = await response.json();
        console.log("User data received:", userData);
        setUser({
          id: userData.id,
          email: userData.email,
          role: userData.role || "student", // Default to student if role is missing
        });
      } else {
        const errorText = await response.text();
        console.error("Failed to fetch user, status:", response.status);
        console.error("Error response:", errorText);
        localStorage.removeItem("access_token");
        setUser(null);
      }
    } catch (error) {
      console.error("Failed to fetch user:", error);
      localStorage.removeItem("access_token");
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (token: string) => {
    try {
      console.log("Login called with token:", token.substring(0, 20) + "...");
      localStorage.setItem("access_token", token);
      await fetchUser(token);
    } catch (error) {
      console.error("Login error:", error);
      localStorage.removeItem("access_token");
      setUser(null);
      throw error; // Re-throw so calling code can handle it
    }
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    setUser(null);
  };

  const isAdmin = () => {
    return user?.role === "admin";
  };

  const isStudent = () => {
    return user?.role === "student";
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        login,
        logout,
        isLoading,
        isAdmin,
        isStudent,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
};
