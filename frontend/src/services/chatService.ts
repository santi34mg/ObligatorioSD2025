/**
 * Chat service - handles all chat-related API calls
 */

import { apiGet, apiPost } from "@/lib/api";

// Types
export interface Chat {
  id: number;
  name: string;
  avatar: string;
  lastMessage: string;
  timestamp: string;
  unread: number;
  online: boolean;
  userId?: string;
  participantIds?: string[];
}

export interface Message {
  id: number;
  chatId: number;
  senderId: string;
  text: string;
  timestamp: string;
  isMine: boolean;
  createdAt?: string;
}

export interface SendMessageRequest {
  chatId: number;
  text: string;
}

export interface CreateChatRequest {
  participantIds: string[];
  name?: string;
}

/**
 * Fetch all chats for the current user
 */
export async function fetchChats(): Promise<Chat[]> {
  try {
    const chats = await apiGet<Chat[]>("/communication/chats");
    return chats;
  } catch (error) {
    console.error("Error fetching chats:", error);
    throw error;
  }
}

/**
 * Fetch messages for a specific chat
 */
export async function fetchMessages(chatId: number): Promise<Message[]> {
  try {
    const messages = await apiGet<Message[]>(
      `/communication/chats/${chatId}/messages`
    );
    return messages;
  } catch (error) {
    console.error(`Error fetching messages for chat ${chatId}:`, error);
    throw error;
  }
}

/**
 * Send a message to a chat
 */
export async function sendMessage(
  request: SendMessageRequest
): Promise<Message> {
  try {
    const message = await apiPost<Message>(
      `/communication/chats/${request.chatId}/messages`,
      { text: request.text }
    );
    return message;
  } catch (error) {
    console.error("Error sending message:", error);
    throw error;
  }
}

/**
 * Create a new chat
 */
export async function createChat(request: CreateChatRequest): Promise<Chat> {
  try {
    const chat = await apiPost<Chat>("/communication/chats", request);
    return chat;
  } catch (error) {
    console.error("Error creating chat:", error);
    throw error;
  }
}

/**
 * Mark messages as read in a chat
 */
export async function markMessagesAsRead(chatId: number): Promise<void> {
  try {
    await apiPost(`/communication/chats/${chatId}/read`, {});
  } catch (error) {
    console.error(`Error marking messages as read for chat ${chatId}:`, error);
    throw error;
  }
}

/**
 * Get chat details
 */
export async function getChatDetails(chatId: number): Promise<Chat> {
  try {
    const chat = await apiGet<Chat>(`/communication/chats/${chatId}`);
    return chat;
  } catch (error) {
    console.error(`Error fetching chat details for ${chatId}:`, error);
    throw error;
  }
}
