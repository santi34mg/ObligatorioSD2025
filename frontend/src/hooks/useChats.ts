/**
 * Custom hook for managing chat data and operations
 */

import { useState, useEffect, useCallback } from "react";
import { useAuth } from "@/contexts/AuthContext";
import {
  fetchChats,
  fetchMessages,
  sendMessage,
  markMessagesAsRead,
  type Chat,
  type Message,
  type SendMessageRequest,
} from "@/services/chatService";
import { toast } from "sonner";

export function useChats() {
  const { user } = useAuth();
  const [chats, setChats] = useState<Chat[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load chats on mount
  const loadChats = useCallback(async () => {
    if (!user) return;

    setIsLoading(true);
    setError(null);

    try {
      const data = await fetchChats();
      setChats(data);
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to load chats";
      setError(errorMessage);
      toast.error("Failed to load chats");
      console.error("Error loading chats:", err);
    } finally {
      setIsLoading(false);
    }
  }, [user]);

  useEffect(() => {
    loadChats();
  }, [loadChats]);

  // Refresh chats
  const refreshChats = useCallback(() => {
    return loadChats();
  }, [loadChats]);

  return {
    chats,
    isLoading,
    error,
    refreshChats,
  };
}

export function useChatMessages(chatId: number | null) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load messages for a chat
  const loadMessages = useCallback(async () => {
    if (!chatId) {
      setMessages([]);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const data = await fetchMessages(chatId);
      setMessages(data);

      // Mark messages as read
      await markMessagesAsRead(chatId);
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to load messages";
      setError(errorMessage);
      toast.error("Failed to load messages");
      console.error("Error loading messages:", err);
    } finally {
      setIsLoading(false);
    }
  }, [chatId]);

  useEffect(() => {
    loadMessages();
  }, [loadMessages]);

  // Send a message
  const sendChatMessage = useCallback(
    async (text: string) => {
      if (!chatId || !text.trim()) return;

      try {
        const request: SendMessageRequest = {
          chatId,
          text: text.trim(),
        };

        const newMessage = await sendMessage(request);

        // Add the new message to the list
        setMessages((prev) => [...prev, newMessage]);
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "Failed to send message";
        toast.error(errorMessage);
        console.error("Error sending message:", err);
        throw err;
      }
    },
    [chatId]
  );

  // Add a message to the list (for WebSocket updates)
  const addMessage = useCallback((message: Message) => {
    setMessages((prev) => {
      // Avoid duplicates
      if (prev.some((m) => m.id === message.id)) {
        return prev;
      }
      return [...prev, message];
    });
  }, []);

  return {
    messages,
    isLoading,
    error,
    sendMessage: sendChatMessage,
    addMessage,
    refreshMessages: loadMessages,
  };
}
