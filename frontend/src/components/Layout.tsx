import { useState } from "react";
import Header from "./header/Header";
import { SidebarProvider } from "@/components/ui/sidebar";
import ChatSidebar from "./chat/ChatSidebar";

export function Layout({ children }: { children: React.ReactNode }) {
  const [isChatSidebarOpen, setIsChatSidebarOpen] = useState(false);

  const toggleChatSidebar = () => {
    setIsChatSidebarOpen(!isChatSidebarOpen);
  };

  return (
    <div className="flex flex-col overflow-hidden w-full h-screen bg-background">
      <Header />
      <SidebarProvider
        open={isChatSidebarOpen}
        onOpenChange={setIsChatSidebarOpen}
      >
        <div className="flex flex-1 overflow-hidden relative">
          <main className="flex-1 relative">{children}</main>
          <ChatSidebar toggleChatSidebar={toggleChatSidebar} />
        </div>
      </SidebarProvider>
    </div>
  );
}
