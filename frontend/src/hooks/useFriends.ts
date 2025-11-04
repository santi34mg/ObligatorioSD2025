/**
 * Custom hook for managing friends data
 */

import { useState, useEffect, useCallback } from "react";
import { useAuth } from "@/contexts/AuthContext";
import {
  fetchFriends,
  type Friendship,
  type FriendsList,
} from "@/services/friendshipService";

export function useFriends(statusFilter?: "pending" | "accepted" | "blocked") {
  const { user } = useAuth();
  const [friends, setFriends] = useState<Friendship[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load friends on mount
  const loadFriends = useCallback(async () => {
    if (!user) return;

    setIsLoading(true);
    setError(null);

    try {
      const data: FriendsList = await fetchFriends(statusFilter);
      setFriends(data.friends);
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to load friends";
      setError(errorMessage);
      console.error("Error loading friends:", err);
    } finally {
      setIsLoading(false);
    }
  }, [user, statusFilter]);

  useEffect(() => {
    loadFriends();
  }, [loadFriends]);

  // Refresh friends
  const refreshFriends = useCallback(() => {
    return loadFriends();
  }, [loadFriends]);

  return {
    friends,
    isLoading,
    error,
    refreshFriends,
  };
}
