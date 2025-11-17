/**
 * Content Service - Handles API calls related to posts/documents
 */

import { apiGet } from "@/lib/api";

export interface PostUser {
  name: string;
  avatar: string;
}

export interface PostResponse {
  id: number;
  user: PostUser;
  date: string; // ISO date string from backend
  title: string;
  content: string;
  commentCount: number;
  likes: number;
  image?: string;
}

/**
 * Fetch all posts from the content service
 */
export async function getPosts(
  skip: number = 0,
  limit: number = 20
): Promise<PostResponse[]> {
  const params = new URLSearchParams({
    skip: skip.toString(),
    limit: limit.toString(),
  });

  const response = await apiGet<{ posts: PostResponse[]; total: number }>(
    `/api/content/posts?${params}`
  );
  return response.posts;
}

/**
 * Helper to convert backend post response to frontend Post type with Date objects
 */
export function convertPostDates(post: PostResponse) {
  return {
    ...post,
    date: new Date(post.date),
  };
}
