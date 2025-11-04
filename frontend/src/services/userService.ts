/**
 * User service for fetching user data
 */

import { apiGet } from "@/lib/api";

export interface User {
  id: string;
  email: string;
  is_active: boolean;
  is_superuser: boolean;
  is_verified: boolean;
}

interface UserPublicInfo {
  id: string;
  email: string;
  is_active: boolean;
  is_verified: boolean;
}

interface UserListResponse {
  users: UserPublicInfo[];
  total: number;
  page: number;
  page_size: number;
}

/**
 * Fetch all users from the users-service
 * Returns active and verified users only
 */
export async function fetchAllUsers(): Promise<User[]> {
  try {
    const response = await apiGet<UserListResponse>(
      "/api/users/list?page=1&page_size=100&is_active=true&is_verified=true"
    );

    // Map backend UserPublicInfo to frontend User interface
    return response.users.map((user) => ({
      id: user.id,
      email: user.email,
      is_active: user.is_active,
      is_superuser: false, // Not included in public info
      is_verified: user.is_verified,
    }));
  } catch (error) {
    console.error("Failed to fetch users list:", error);
    throw error;
  }
}

/**
 * Fetch current user profile
 */
export async function fetchCurrentUser(): Promise<User> {
  return apiGet<User>("/users/me");
}
