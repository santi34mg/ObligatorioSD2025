import { Plus, FileText, MessageSquare } from "lucide-react";
import { useNavigate } from "react-router-dom";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";

export function FloatingActionButton() {
  const navigate = useNavigate();

  const handleDocument = () => {
    navigate("/upload/document");
  };

  const handleDiscussion = () => {
    console.log("Discussion clicked");
    // Add your discussion creation logic here
  };

  return (
    <div className="fixed bottom-6 right-6 z-50">
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button
            size="lg"
            className="h-14 w-14 rounded-full shadow-xl/20 hover:shadow-xl/30 transition-shadow bg-white hover:bg-gray-50"
          >
            <Plus className="h-10 w-10 text-black" strokeWidth={3} />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-48">
          <DropdownMenuItem onClick={handleDocument} className="cursor-pointer">
            <FileText className="mr-2 h-4 w-4" />
            <span>Document</span>
          </DropdownMenuItem>
          <DropdownMenuItem
            onClick={handleDiscussion}
            className="cursor-pointer"
          >
            <MessageSquare className="mr-2 h-4 w-4" />
            <span>Discussion</span>
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
}
