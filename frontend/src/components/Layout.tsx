import Header from "./header/Header";
import { ChatSidebar } from "./chat/ChatSidebar";

interface LayoutProps {
  isChatOpen: boolean;
  toggleChat: () => void;
}

export function Layout({
  layoutProps,
  children,
}: {
  layoutProps: LayoutProps;
  children: React.ReactNode;
}) {
  return (
    <div className="flex flex-col w-full h-full bg-background">
      <Header />
      <div className="flex flex-1 overflow-hidden">
        <div
          className={`flex-1 transition-all duration-300 ease-in-out ${
            layoutProps.isChatOpen ? "mr-80" : "mr-0"
          }`}
        >
          {children}
        </div>
        <ChatSidebar isOpen={layoutProps.isChatOpen} />
      </div>
    </div>
  );
}
