import { Feed } from "@/components/contentarea/FeedList";
import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area";

export function ContentArea() {
  return (
    <ScrollArea className="max-w-2xl mx-auto py-6 px-4 h-full [&>[data-slot=scroll-area-scrollbar]]:hidden">
      <Feed />
      <ScrollBar className="hidden" />
    </ScrollArea>
  );
}
