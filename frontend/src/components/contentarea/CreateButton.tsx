import { Plus, FileText, MessageSquare } from "lucide-react";
import { useNavigate } from "react-router-dom";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";

export function FloatingActionButton() {
  const navigate = useNavigate();

  const handleDocument = () => {
    navigate("/upload/document");
  };

  const handleDiscussion = () => {
    toast.info("Sorry, this feature is coming soon!");
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          size="lg"
          className="rounded-full shadow-md hover:shadow-lg transition-shadow bg-primary hover:bg-primary/90"
        >
          <Plus className="h-5 w-5 mr-2" strokeWidth={2.5} />
          <span className="font-medium">Create</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start" className="w-48">
        <DropdownMenuItem onClick={handleDocument} className="cursor-pointer">
          <FileText className="mr-2 h-4 w-4" />
          <span>Document</span>
        </DropdownMenuItem>
        <DropdownMenuItem onClick={handleDiscussion} className="cursor-pointer">
          <MessageSquare className="mr-2 h-4 w-4" />
          <span>Discussion</span>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
