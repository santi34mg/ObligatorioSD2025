/**
 * Admin service for role management and user administration
 */

import { type UserRole } from "@/lib/roles";

const API_BASE_URL = "http://localhost/api";

interface User {
  id: string;
  email: string;
  role: UserRole;
  is_active: boolean;
  is_verified: boolean;
}

interface UserListResponse {
  users: User[];
  total: number;
  page: number;
  page_size: number;
}

interface UpdateRoleRequest {
  role: UserRole;
}

/**
 * Get list of all users with pagination
 */
export async function getUsersList(
  page: number = 1,
  pageSize: number = 20,
  filters?: {
    email_filter?: string;
    is_active?: boolean;
    is_verified?: boolean;
  }
): Promise<UserListResponse> {
  const token = localStorage.getItem("access_token");
  if (!token) {
    throw new Error("No authentication token found");
  }

  const params = new URLSearchParams({
    page: page.toString(),
    page_size: pageSize.toString(),
  });

  if (filters?.email_filter) {
    params.append("email_filter", filters.email_filter);
  }
  if (filters?.is_active !== undefined) {
    params.append("is_active", filters.is_active.toString());
  }
  if (filters?.is_verified !== undefined) {
    params.append("is_verified", filters.is_verified.toString());
  }

  const response = await fetch(`${API_BASE_URL}/users/list?${params}`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Failed to fetch users list");
  }

  return response.json();
}

/**
 * Update a user's role (admin only)
 */
export async function updateUserRole(
  userId: string,
  newRole: UserRole
): Promise<User> {
  const token = localStorage.getItem("access_token");
  if (!token) {
    throw new Error("No authentication token found");
  }

  const body: UpdateRoleRequest = { role: newRole };

  const response = await fetch(`${API_BASE_URL}/users/${userId}/role`, {
    method: "PATCH",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Failed to update user role");
  }

  return response.json();
}

/**
 * Get detailed user information
 */
export async function getUserDetails(userId: string): Promise<User> {
  const token = localStorage.getItem("access_token");
  if (!token) {
    throw new Error("No authentication token found");
  }

  const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Failed to fetch user details");
  }

  return response.json();
}
