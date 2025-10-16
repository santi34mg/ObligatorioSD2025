import { Navbar } from "./Navbar";
import { ContentArea } from "./ContentArea";
import { ChatSidebar } from "./ChatSidebar";
interface LayoutProps {
  isChatOpen: boolean;
  toggleChat: () => void;
}
export function Layout({ isChatOpen, toggleChat }: LayoutProps) {
  return (
    <div className="flex flex-col w-full h-screen bg-background">
      <Navbar toggleChat={toggleChat} isChatOpen={isChatOpen} />
      <div className="flex flex-1 overflow-hidden">
        <div
          className={`flex-1 transition-all duration-300 ease-in-out ${
            isChatOpen ? "mr-80" : "mr-0"
          }`}
        >
          <ContentArea />
        </div>
        <ChatSidebar isOpen={isChatOpen} />
      </div>
    </div>
  );
}
