import { createContext, useContext, useState, useEffect, useRef } from "react";
import type { ReactNode } from "react";
import { mockChats } from "@/components/chat/Mockchats";
import { useChats, useChatMessages } from "@/hooks/useChats";
import { toast } from "sonner";
import { useToastContainer } from "@/contexts/ToastContext";

interface ChatContextType {
  // Chat list state
  chats: any[];
  isLoadingChats: boolean;
  displayChats: any[];
  filteredChats: any[];

  // Selected chat state
  selectedChat: any;
  setSelectedChat: (chat: any) => void;
  handleChatSelect: (chat: any) => void;

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
  const [selectedChat, setSelectedChat] = useState<
    (typeof mockChats)[0] | null
  >(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [messageInput, setMessageInput] = useState("");
  const messagesAreaRef = useRef<HTMLDivElement>(null);
  const { setToastContainer } = useToastContainer();

  // Use the custom hook for messages
  const {
    messages,
    isLoading: isLoadingMessages,
    sendMessage,
  } = useChatMessages(selectedChat?.id ?? null);

  // Use real chats if available, otherwise fall back to mock data
  const displayChats = chats.length > 0 ? chats : mockChats;

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

  // Set the first chat as selected when chats are loaded
  useEffect(() => {
    if (displayChats.length > 0 && !selectedChat) {
      setSelectedChat(displayChats[0]);
    }
  }, [displayChats, selectedChat]);

  const filteredChats = displayChats.filter((chat) =>
    chat.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleSendMessage = async () => {
    if (!messageInput.trim() || !selectedChat) return;

    try {
      await sendMessage(messageInput);
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

  const handleChatSelect = (chat: (typeof mockChats)[0]) => {
    setSelectedChat(chat);
  };

  const value: ChatContextType = {
    chats,
    isLoadingChats,
    displayChats,
    filteredChats,
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
