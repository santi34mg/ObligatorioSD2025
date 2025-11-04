import { MessageSquare } from "lucide-react";
import { Button } from "@/components/ui/button";

interface FloatingChatButtonProps {
  onClick: () => void;
  isOpen: boolean;
}

export function FloatingChatButton({
  onClick,
  isOpen,
}: FloatingChatButtonProps) {
  if (isOpen) return null; // Hide button when chat is open

  return (
    <div className="fixed bottom-6 right-22 z-50">
      <Button
        size="lg"
        onClick={onClick}
        className="h-14 w-14 rounded-full shadow-xl/20 hover:shadow-xl/30 transition-shadow bg-white hover:bg-gray-50"
      >
        <MessageSquare className="h-6 w-6 text-black" strokeWidth={2} />
      </Button>
    </div>
  );
}
