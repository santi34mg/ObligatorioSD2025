/**
 * Friendship service for managing user friendships
 */

import { apiGet, apiPost, apiDelete } from "@/lib/api";

export interface Friendship {
  friendship_id: string;
  friend_user_id: string;
  friend_email: string;
  status: "pending" | "accepted" | "blocked";
  created_at: string;
  updated_at: string;
}

export interface FriendsList {
  friends: Friendship[];
  total: number;
}

export interface FriendRequestData {
  friend_id: string;
}

/**
 * Fetch all friends with optional status filter
 */
export async function fetchFriends(
  statusFilter?: "pending" | "accepted" | "blocked"
): Promise<FriendsList> {
  const endpoint = statusFilter
    ? `/friendships/?status_filter=${statusFilter}`
    : "/friendships/";
  return apiGet<FriendsList>(endpoint);
}

/**
 * Send a friend request
 */
export async function sendFriendRequest(friendId: string): Promise<Friendship> {
  return apiPost<Friendship>("/friendships/request", { friend_id: friendId });
}

/**
 * Accept a friend request
 */
export async function acceptFriendRequest(
  friendshipId: string
): Promise<Friendship> {
  return apiPost<Friendship>(`/friendships/${friendshipId}/accept`, {});
}

/**
 * Block a user
 */
export async function blockUser(friendshipId: string): Promise<Friendship> {
  return apiPost<Friendship>(`/friendships/${friendshipId}/block`, {});
}

/**
 * Remove a friend / unfriend
 */
export async function removeFriend(friendId: string): Promise<void> {
  return apiDelete<void>(`/friendships/${friendId}`);
}
