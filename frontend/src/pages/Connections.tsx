import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Send,
  Search,
  MoreVertical,
  Loader2,
  Users,
  UserPlus,
} from "lucide-react";
import { ChatProvider, useChatContext } from "@/contexts/ChatContext";
import { Separator } from "@/components/ui/separator";

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
  const {
    filteredFriendChats,
    filteredNonFriendChats,
    selectedChat,
    handleChatSelect,
  } = useChatContext();

  return (
    <ScrollArea className="flex-1">
      <div className="p-3">
        {/* Friends Section */}
        <div className="mb-4">
          <div className="flex items-center gap-2 px-2 py-2 text-xs font-semibold text-muted-foreground uppercase">
            <Users className="h-4 w-4" />
            <span>Friends ({filteredFriendChats.length})</span>
          </div>
          <div className="divide-y">
            {filteredFriendChats.length === 0 ? (
              <div className="p-4 text-center text-sm text-muted-foreground">
                No friends yet. Add friends below!
              </div>
            ) : (
              filteredFriendChats.map((chat) => (
                <button
                  key={chat.id}
                  onClick={() => handleChatSelect(chat)}
                  className={`w-full p-4 flex items-center gap-3 hover:bg-accent transition-colors rounded-lg ${
                    selectedChat?.id === chat.id ? "bg-accent" : ""
                  }`}
                >
                  <div className="relative">
                    <Avatar className="h-12 w-12">
                      <AvatarImage src={chat.avatar} alt={chat.name} />
                      <AvatarFallback className="text-base">
                        {chat.name.charAt(0).toUpperCase()}
                      </AvatarFallback>
                    </Avatar>
                    {chat.online && (
                      <div className="absolute bottom-0 right-0 w-3 h-3 bg-green-500 border-2 border-background rounded-full" />
                    )}
                  </div>
                  <div className="flex-1 text-left min-w-0">
                    <span className="font-semibold truncate block">
                      {chat.name}
                    </span>
                    <p className="text-xs text-muted-foreground truncate">
                      {chat.email}
                    </p>
                  </div>
                </button>
              ))
            )}
          </div>
        </div>

        <Separator className="my-4" />

        {/* Non-Friends Section */}
        <div>
          <div className="flex items-center gap-2 px-2 py-2 text-xs font-semibold text-muted-foreground uppercase">
            <UserPlus className="h-4 w-4" />
            <span>Other Users ({filteredNonFriendChats.length})</span>
          </div>
          <div className="divide-y">
            {filteredNonFriendChats.length === 0 ? (
              <div className="p-4 text-center text-sm text-muted-foreground">
                No other users found
              </div>
            ) : (
              filteredNonFriendChats.map((chat) => (
                <button
                  key={chat.id}
                  onClick={() => handleChatSelect(chat)}
                  className={`w-full p-4 flex items-center gap-3 hover:bg-accent transition-colors rounded-lg ${
                    selectedChat?.id === chat.id ? "bg-accent" : ""
                  }`}
                >
                  <div className="relative">
                    <Avatar className="h-12 w-12">
                      <AvatarImage src={chat.avatar} alt={chat.name} />
                      <AvatarFallback className="text-base">
                        {chat.name.charAt(0).toUpperCase()}
                      </AvatarFallback>
                    </Avatar>
                  </div>
                  <div className="flex-1 text-left min-w-0">
                    <span className="font-semibold truncate block">
                      {chat.name}
                    </span>
                    <p className="text-xs text-muted-foreground truncate">
                      {chat.email}
                    </p>
                  </div>
                  <Button variant="ghost" size="sm" className="ml-auto">
                    <UserPlus className="h-4 w-4" />
                  </Button>
                </button>
              ))
            )}
          </div>
        </div>
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

  if (!selectedChat) return null;

  return (
    <div className="p-4 border-b flex items-center justify-between bg-background">
      <div className="flex items-center gap-3">
        <div className="relative">
          <Avatar className="h-10 w-10">
            <AvatarImage src={selectedChat.avatar} alt={selectedChat.name} />
            <AvatarFallback>
              {selectedChat.name.charAt(0).toUpperCase()}
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

  if (!selectedChat) return null;

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
                        {selectedChat.name.charAt(0).toUpperCase()}
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
      <div className="flex items-center justify-center h-full">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="flex h-full bg-background border-t">
      <ChatListSideBar />
      {!selectedChat ? (
        <div className="flex-1 flex items-center justify-center">
          <p className="text-muted-foreground">
            Select a chat to start messaging
          </p>
        </div>
      ) : (
        <ChatArea />
      )}
    </div>
  );
}

export default function Connections() {
  return (
    <div className="h-full overflow-hidden">
      <ChatProvider>
        <ChatsContent />
      </ChatProvider>
    </div>
  );
}
