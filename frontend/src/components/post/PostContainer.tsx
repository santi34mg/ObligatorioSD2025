import { MessageCircle, Heart, Share2 } from "lucide-react";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
} from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";

interface User {
  name: string;
  avatar: string;
}

interface Post {
  id: number;
  user: User;
  date: Date;
  content: string;
  commentCount: number;
  likes: number;
  image?: string;
}

interface PostContainerProps {
  post: Post;
}

export function PostContainer({ post }: PostContainerProps) {
  const formattedDate = new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(post.date);

  // Get initials for avatar fallback
  const getInitials = (name: string) => {
    return name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase();
  };

  return (
    <Card className="overflow-hidden">
      <CardHeader className="pb-3">
        <div className="flex items-center gap-3">
          <Avatar className="size-10">
            <AvatarImage src={post.user.avatar} alt={post.user.name} />
            <AvatarFallback>{getInitials(post.user.name)}</AvatarFallback>
          </Avatar>
          <div className="flex flex-col">
            <span className="font-semibold text-sm">{post.user.name}</span>
            <span className="text-xs text-muted-foreground">
              {formattedDate}
            </span>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4 pb-3">
        <p className="text-sm text-foreground">{post.content}</p>
        {post.image && (
          <div className="rounded-md overflow-hidden -mx-6">
            <img
              src={post.image}
              alt="Post attachment"
              className="w-full h-auto object-cover"
            />
          </div>
        )}
      </CardContent>

      <Separator />

      <CardFooter className="pt-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            className="gap-1.5 text-muted-foreground hover:text-primary"
          >
            <Heart size={18} />
            <span className="text-sm">{post.likes}</span>
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className="gap-1.5 text-muted-foreground hover:text-primary"
          >
            <MessageCircle size={18} />
            <span className="text-sm">{post.commentCount}</span>
          </Button>
        </div>
        <Button
          variant="ghost"
          size="icon-sm"
          className="text-muted-foreground hover:text-primary"
        >
          <Share2 size={18} />
        </Button>
      </CardFooter>
    </Card>
  );
}

// Export as PostCard for backward compatibility
export { PostContainer as PostCard };
