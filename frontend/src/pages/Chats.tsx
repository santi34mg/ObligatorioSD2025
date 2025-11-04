import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Send, Search, MoreVertical, Loader2 } from "lucide-react";
import { ChatProvider, useChatContext } from "@/contexts/ChatContext";

function ChatListSideBar() {
  return (
    <div className="w-[400px] border-r flex flex-col">
      <ChatListHeader />
      <ChatList />
    </div>
  );
}

function ChatListHeader() {
  const { searchQuery, setSearchQuery } = useChatContext();

  return (
    <div className="p-4 border-b">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold">Messages</h2>
        <Button variant="ghost" size="icon">
          <MoreVertical className="h-5 w-5" />
        </Button>
      </div>
      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search chats..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="pl-9"
        />
      </div>
    </div>
  );
}

function ChatList() {
  const { filteredChats, selectedChat, handleChatSelect } = useChatContext();

  return (
    <ScrollArea className="flex-1">
      <div className="divide-y">
        {filteredChats.map((chat) => (
          <button
            key={chat.id}
            onClick={() => handleChatSelect(chat)}
            className={`w-full p-4 flex items-center gap-3 hover:bg-accent transition-colors ${
              selectedChat?.id === chat.id ? "bg-accent" : ""
            }`}
          >
            <div className="relative">
              <Avatar className="h-14 w-14">
                <AvatarImage src={chat.avatar} alt={chat.name} />
                <AvatarFallback className="text-lg">
                  {chat.name
                    .split(" ")
                    .map((n: string) => n[0])
                    .join("")}
                </AvatarFallback>
              </Avatar>
              {chat.online && (
                <div className="absolute bottom-0 right-0 w-4 h-4 bg-green-500 border-2 border-background rounded-full" />
              )}
            </div>
            <div className="flex-1 text-left min-w-0">
              <div className="flex items-center justify-between mb-1">
                <span className="font-semibold truncate">{chat.name}</span>
                <span className="text-xs text-muted-foreground whitespace-nowrap ml-2">
                  {chat.timestamp}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <p className="text-sm text-muted-foreground truncate">
                  {chat.lastMessage}
                </p>
                {chat.unread > 0 && (
                  <span className="ml-2 bg-primary text-primary-foreground text-xs font-semibold rounded-full h-5 w-5 flex items-center justify-center">
                    {chat.unread}
                  </span>
                )}
              </div>
            </div>
          </button>
        ))}
      </div>
    </ScrollArea>
  );
}

function ChatArea() {
  return (
    <div className="flex-1 flex flex-col">
      <ChatAreaHeader />
      <ChatMessagesArea />
      <MessageInput />
    </div>
  );
}

function ChatAreaHeader() {
  const { selectedChat } = useChatContext();

  return (
    <div className="p-4 border-b flex items-center justify-between bg-background">
      <div className="flex items-center gap-3">
        <div className="relative">
          <Avatar className="h-10 w-10">
            <AvatarImage src={selectedChat.avatar} alt={selectedChat.name} />
            <AvatarFallback>
              {selectedChat.name
                .split(" ")
                .map((n: string) => n[0])
                .join("")}
            </AvatarFallback>
          </Avatar>
          {selectedChat.online && (
            <div className="absolute bottom-0 right-0 w-3 h-3 bg-green-500 border-2 border-background rounded-full" />
          )}
        </div>
        <div>
          <h3 className="font-semibold">{selectedChat.name}</h3>
          <p className="text-xs text-muted-foreground">
            {selectedChat.online ? "Active now" : "Offline"}
          </p>
        </div>
      </div>
    </div>
  );
}

function ChatMessagesArea() {
  const { messages, isLoadingMessages, selectedChat, messagesAreaRef } =
    useChatContext();

  return (
    <div ref={messagesAreaRef} className="flex-1 relative overflow-hidden">
      <ScrollArea className="h-full p-4">
        {isLoadingMessages ? (
          <div className="flex items-center justify-center h-full">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        ) : messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <p className="text-muted-foreground">
              No messages yet. Start the conversation!
            </p>
          </div>
        ) : (
          <div className="space-y-4 max-w-4xl mx-auto">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${
                  message.isMine ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`flex gap-2 max-w-[70%] ${
                    message.isMine ? "flex-row-reverse" : "flex-row"
                  }`}
                >
                  {!message.isMine && (
                    <Avatar className="h-8 w-8 mt-auto">
                      <AvatarImage
                        src={selectedChat.avatar}
                        alt={selectedChat.name}
                      />
                      <AvatarFallback className="text-xs">
                        {selectedChat.name
                          .split(" ")
                          .map((n: string) => n[0])
                          .join("")}
                      </AvatarFallback>
                    </Avatar>
                  )}
                  <div>
                    <div
                      className={`rounded-3xl px-4 py-2 ${
                        message.isMine
                          ? "bg-primary text-primary-foreground"
                          : "bg-accent"
                      }`}
                    >
                      <p className="text-sm">{message.text}</p>
                    </div>
                    <p
                      className={`text-xs text-muted-foreground mt-1 px-2 ${
                        message.isMine ? "text-right" : "text-left"
                      }`}
                    >
                      {message.timestamp}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </ScrollArea>
    </div>
  );
}

function MessageInput() {
  const { messageInput, setMessageInput, handleSendMessage, handleKeyPress } =
    useChatContext();

  return (
    <div className="p-4 border-t bg-background">
      <div className="max-w-4xl mx-auto flex items-center gap-2">
        <Input
          placeholder="Type a message..."
          value={messageInput}
          onChange={(e) => setMessageInput(e.target.value)}
          onKeyPress={handleKeyPress}
          className="flex-1"
        />
        <Button
          onClick={handleSendMessage}
          disabled={!messageInput.trim()}
          size="icon"
        >
          <Send className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}

function ChatsContent() {
  const { isLoadingChats, selectedChat } = useChatContext();

  if (isLoadingChats) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-4rem)]">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (!selectedChat) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-4rem)]">
        <p className="text-muted-foreground">No chats available</p>
      </div>
    );
  }

  return (
    <div className="flex h-[calc(100vh-4rem)] bg-background border-t">
      <ChatListSideBar />
      <ChatArea />
    </div>
  );
}

export default function Chats() {
  return (
    <ChatProvider>
      <ChatsContent />
    </ChatProvider>
  );
}
