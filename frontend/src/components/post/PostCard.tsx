import { MessageCircle, Heart, Share2 } from "lucide-react";
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
interface PostCardProps {
  post: Post;
}
export function PostCard({ post }: PostCardProps) {
  const formattedDate = new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(post.date);
  return (
    <div className="bg-white rounded-lg shadow border border-border overflow-hidden">
      <div className="p-4">
        <div className="flex items-center mb-3">
          <img
            src={post.user.avatar}
            alt={post.user.name}
            className="w-10 h-10 rounded-full mr-3 object-cover"
          />
          <div>
            <h3 className="font-semibold text-primary">{post.user.name}</h3>
            <p className="text-xs text-muted-foreground">{formattedDate}</p>
          </div>
        </div>
        <p className="text-foreground mb-4">{post.content}</p>
        {post.image && (
          <div className="mb-4 -mx-4">
            <img
              src={post.image}
              alt="Post attachment"
              className="w-full h-auto"
            />
          </div>
        )}
        <div className="flex items-center justify-between pt-3 border-t border-border">
          <div className="flex items-center space-x-4">
            <button className="flex items-center text-muted-foreground hover:text-primary transition-colors">
              <Heart size={18} className="mr-1" />
              <span className="text-sm">{post.likes}</span>
            </button>
            <button className="flex items-center text-muted-foreground hover:text-primary transition-colors">
              <MessageCircle size={18} className="mr-1" />
              <span className="text-sm">{post.commentCount}</span>
            </button>
          </div>
          <button className="text-muted-foreground hover:text-primary transition-colors">
            <Share2 size={18} />
          </button>
        </div>
      </div>
    </div>
  );
}
