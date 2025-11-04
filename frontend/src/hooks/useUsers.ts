/**
 * Custom hook for managing users data
 */

import { useState, useEffect, useCallback } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { fetchAllUsers, type User } from "@/services/userService";

export function useUsers() {
  const { user } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load users on mount
  const loadUsers = useCallback(async () => {
    if (!user) return;

    setIsLoading(true);
    setError(null);

    try {
      const data = await fetchAllUsers();
      setUsers(data);
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to load users";
      setError(errorMessage);
      console.error("Error loading users:", err);
    } finally {
      setIsLoading(false);
    }
  }, [user]);

  useEffect(() => {
    loadUsers();
  }, [loadUsers]);

  // Refresh users
  const refreshUsers = useCallback(() => {
    return loadUsers();
  }, [loadUsers]);

  return {
    users,
    isLoading,
    error,
    refreshUsers,
  };
}
