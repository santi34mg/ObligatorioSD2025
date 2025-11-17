import { MessageCircle, Heart, Share2, FileText, Download } from "lucide-react";
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

export interface Post {
  id: number;
  user: User;
  date: Date;
  title: string;
  content: string;
  commentCount: number;
  likes: number;
  image?: string;
  fileUrl?: string;
  fileName?: string;
  fileType?: string;
}

export function PostContainer({ post }: { post: Post }) {
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

  // Get file icon based on file type
  const getFileIcon = (fileType?: string) => {
    if (!fileType) return <FileText className="h-8 w-8" />;

    if (fileType.includes("pdf")) {
      return <FileText className="h-8 w-8 text-red-500" />;
    } else if (fileType.includes("word") || fileType.includes("document")) {
      return <FileText className="h-8 w-8 text-blue-500" />;
    } else if (fileType.includes("sheet") || fileType.includes("excel")) {
      return <FileText className="h-8 w-8 text-green-500" />;
    } else if (
      fileType.includes("presentation") ||
      fileType.includes("powerpoint")
    ) {
      return <FileText className="h-8 w-8 text-orange-500" />;
    } else if (fileType.includes("video")) {
      return <FileText className="h-8 w-8 text-purple-500" />;
    } else if (fileType.includes("audio")) {
      return <FileText className="h-8 w-8 text-pink-500" />;
    }
    return <FileText className="h-8 w-8" />;
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
        {post.title && (
          <h3 className="text-lg font-semibold text-foreground">
            {post.title}
          </h3>
        )}
        <p className="text-sm text-foreground whitespace-pre-wrap">
          {post.content}
        </p>
        {post.image && (
          <div className="rounded-md overflow-hidden -mx-6">
            <img
              src={post.image}
              alt="Post attachment"
              className="w-full h-auto object-cover"
            />
          </div>
        )}
        {post.fileUrl && !post.image && (
          <div className="border rounded-lg p-4 bg-muted/30 hover:bg-muted/50 transition-colors">
            <a
              href={post.fileUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-3 group"
            >
              <div className="flex-shrink-0">{getFileIcon(post.fileType)}</div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-foreground group-hover:text-primary transition-colors truncate">
                  {post.fileName || "Attached file"}
                </p>
                {post.fileType && (
                  <p className="text-xs text-muted-foreground">
                    {post.fileType.split("/")[1]?.toUpperCase() || "File"}
                  </p>
                )}
              </div>
              <Button
                variant="ghost"
                size="icon-sm"
                className="flex-shrink-0 text-muted-foreground group-hover:text-primary"
                onClick={(e) => {
                  e.preventDefault();
                  window.open(post.fileUrl, "_blank");
                }}
              >
                <Download className="h-4 w-4" />
              </Button>
            </a>
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
