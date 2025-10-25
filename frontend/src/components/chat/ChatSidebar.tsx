import { Send } from "lucide-react";
interface ChatSidebarProps {
  isOpen: boolean;
}
export function ChatSidebar({ isOpen }: ChatSidebarProps) {
  return (
    <div
      className={`fixed top-16 right-0 w-80 h-[calc(100vh-4rem)] bg-white border-l border-border transition-transform duration-300 ease-in-out transform ${
        isOpen ? "translate-x-0" : "translate-x-full"
      }`}
    >
      <div className="flex flex-col h-full">
        <div className="p-4 border-b border-border">
          <h3 className="font-semibold">Chat</h3>
        </div>
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          <ChatMessage
            user="Alex Johnson"
            message="Hey, did you finish the assignment yet?"
            time="10:30 AM"
            isIncoming={true}
          />
          <ChatMessage
            user="You"
            message="Almost done! Just need to complete the last question."
            time="10:32 AM"
            isIncoming={false}
          />
          <ChatMessage
            user="Alex Johnson"
            message="Great! Let me know if you need any help."
            time="10:33 AM"
            isIncoming={true}
          />
        </div>
        <div className="p-4 border-t border-border">
          <div className="flex items-center">
            <input
              type="text"
              placeholder="Type a message..."
              className="flex-1 px-4 py-2 rounded-full border border-input focus:outline-none focus:ring-2 focus:ring-primary/50"
            />
            <button className="ml-2 p-2 rounded-full bg-primary text-primary-foreground">
              <Send size={18} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
interface ChatMessageProps {
  user: string;
  message: string;
  time: string;
  isIncoming: boolean;
}
function ChatMessage({ user, message, time, isIncoming }: ChatMessageProps) {
  return (
    <div className={`flex flex-col ${isIncoming ? "" : "items-end"}`}>
      <div className="text-xs text-muted-foreground mb-1">
        {isIncoming ? user : "You"} • {time}
      </div>
      <div
        className={`max-w-[80%] p-3 rounded-lg ${
          isIncoming
            ? "bg-secondary text-secondary-foreground"
            : "bg-primary text-primary-foreground"
        }`}
      >
        {message}
      </div>
    </div>
  );
}
