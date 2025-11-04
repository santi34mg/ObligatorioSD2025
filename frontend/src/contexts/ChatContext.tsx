import { createContext, useContext, useState, useEffect, useRef } from "react";
import type { ReactNode } from "react";
import { useChats } from "@/hooks/useChats";
import { useFriends } from "@/hooks/useFriends";
import { useUsers } from "@/hooks/useUsers";
import { useAuth } from "@/contexts/AuthContext";
import { toast } from "sonner";
import { useToastContainer } from "@/contexts/ToastContext";

/**
 * Generate avatar URL using UI Avatars service
 */
function getAvatarUrl(email: string): string {
  const name = email.split("@")[0];
  return `https://ui-avatars.com/api/?name=${encodeURIComponent(
    name
  )}&background=random&size=128`;
}

// Chat interface that combines friend data
interface ChatUser {
  id: string;
  name: string;
  email: string;
  avatar: string;
  online: boolean;
  isFriend: boolean;
}

interface ChatContextType {
  // Chat list state
  chats: any[];
  isLoadingChats: boolean;
  friendChats: ChatUser[];
  nonFriendChats: ChatUser[];
  filteredFriendChats: ChatUser[];
  filteredNonFriendChats: ChatUser[];
  hasError: boolean;

  // Selected chat state
  selectedChat: ChatUser | null;
  setSelectedChat: (chat: ChatUser | null) => void;
  handleChatSelect: (chat: ChatUser) => void;

  // Messages state
  messages: any[];
  isLoadingMessages: boolean;

  // Search state
  searchQuery: string;
  setSearchQuery: (query: string) => void;

  // Message input state
  messageInput: string;
  setMessageInput: (input: string) => void;
  handleSendMessage: () => void;
  handleKeyPress: (e: React.KeyboardEvent) => void;

  // Refs
  messagesAreaRef: React.RefObject<HTMLDivElement | null>;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export function ChatProvider({ children }: { children: ReactNode }) {
  const { chats, isLoading: isLoadingChats, refreshChats } = useChats();
  const {
    friends,
    isLoading: isLoadingFriends,
    error: friendsError,
  } = useFriends("accepted");
  const { users, isLoading: isLoadingUsers, error: usersError } = useUsers();
  const { user: currentUser } = useAuth();
  const [selectedChat, setSelectedChat] = useState<ChatUser | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [messageInput, setMessageInput] = useState("");
  const messagesAreaRef = useRef<HTMLDivElement>(null);
  const { setToastContainer } = useToastContainer();

  // Show toast errors when data fetching fails
  useEffect(() => {
    if (friendsError) {
      toast.error("Failed to load friends");
    }
    if (usersError) {
      toast.error("Failed to load users");
    }
  }, [friendsError, usersError]);

  // For now, we'll use empty messages for friend chats
  // TODO: Integrate with a proper messaging service that uses friend UUIDs
  const messages: any[] = [];
  const isLoadingMessages = false;

  // Get friend IDs for filtering
  const friendIds = new Set(friends.map((friend) => friend.friend_user_id));

  // Get current user ID
  const currentUserId = currentUser?.id;

  // Convert friends to chat users (filter out current user just in case)
  const friendChats: ChatUser[] = friends
    .filter((friend) => friend.friend_user_id !== currentUserId)
    .map((friend) => ({
      id: friend.friend_user_id,
      name: friend.friend_email.split("@")[0],
      email: friend.friend_email,
      avatar: getAvatarUrl(friend.friend_email),
      online: false, // TODO: implement online status via WebSocket
      isFriend: true,
    }));

  // Convert non-friend users to chat users (exclude friends and current user)
  const nonFriendChats: ChatUser[] = users
    .filter((user) => !friendIds.has(user.id) && user.id !== currentUserId)
    .map((user) => ({
      id: user.id,
      name: user.email.split("@")[0],
      email: user.email,
      avatar: getAvatarUrl(user.email),
      online: false, // TODO: implement online status via WebSocket
      isFriend: false,
    }));

  // Set the messages area as the toast container
  useEffect(() => {
    if (messagesAreaRef.current) {
      setToastContainer(messagesAreaRef.current);
    }
    // Cleanup: reset to default when component unmounts
    return () => {
      setToastContainer(null);
    };
  }, [setToastContainer]);

  // Set the first friend chat as selected when chats are loaded
  useEffect(() => {
    if (friendChats.length > 0 && !selectedChat) {
      setSelectedChat(friendChats[0]);
    }
  }, [friendChats, selectedChat]);

  const filteredFriendChats = friendChats.filter(
    (chat: ChatUser) =>
      chat.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      chat.email.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const filteredNonFriendChats = nonFriendChats.filter(
    (chat: ChatUser) =>
      chat.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      chat.email.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleSendMessage = async () => {
    if (!messageInput.trim() || !selectedChat) return;

    try {
      // TODO: Implement sending message to friend via messaging service
      toast.info("Message sending not yet implemented for friend chats");
      setMessageInput("");

      // Refresh chats to update last message
      refreshChats();
    } catch (error) {
      console.error("Failed to send message:", error);
      toast.error("Failed to send message");
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleChatSelect = (chat: ChatUser) => {
    setSelectedChat(chat);
  };

  const value: ChatContextType = {
    chats,
    isLoadingChats: isLoadingChats || isLoadingFriends || isLoadingUsers,
    friendChats,
    nonFriendChats,
    filteredFriendChats,
    filteredNonFriendChats,
    hasError: !!friendsError || !!usersError,
    selectedChat,
    setSelectedChat,
    handleChatSelect,
    messages,
    isLoadingMessages,
    searchQuery,
    setSearchQuery,
    messageInput,
    setMessageInput,
    handleSendMessage,
    handleKeyPress,
    messagesAreaRef,
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
}

export function useChatContext() {
  const context = useContext(ChatContext);
  if (context === undefined) {
    throw new Error("useChatContext must be used within a ChatProvider");
  }
  return context;
}
