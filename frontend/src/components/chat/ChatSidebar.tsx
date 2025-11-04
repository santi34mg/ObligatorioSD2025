import {
  Sidebar,
  SidebarContent,
  SidebarHeader,
} from "@/components/ui/sidebar";

export default function ChatSidebar({
  toggleChatSidebar,
}: {
  toggleChatSidebar: () => void;
}) {
  return (
    <Sidebar side="right" collapsible="offcanvas" className="border-l">
      <SidebarHeader>
        <div className="flex items-center justify-between px-4 py-2">
          <h2 className="text-lg font-semibold">Chat Assistant</h2>
          <button
            onClick={toggleChatSidebar}
            className="text-gray-500 hover:text-gray-700"
          >
            ✕
          </button>
        </div>
      </SidebarHeader>
      <SidebarContent>
        <div className="px-4 py-2">
          <p className="text-sm text-gray-600">Chat content goes here...</p>
        </div>
      </SidebarContent>
    </Sidebar>
  );
}
