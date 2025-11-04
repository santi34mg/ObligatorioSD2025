import { PostContainer, type Post } from "../post/PostContainer";
import { useEffect, useState } from "react";
import { Card, CardContent } from "../ui/card";
import { FloatingActionButton } from "../FloatingActionButton";

function EmptyFeedState() {
  return (
    <Card className="border-dashed border-2 bg-muted/30">
      <CardContent className="flex flex-col items-center justify-center py-16 px-6">
        <div className="rounded-full bg-primary/10 p-6 mb-6">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-12 w-12 text-primary"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={1.5}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z"
            />
          </svg>
        </div>
        <h3 className="text-xl font-semibold text-foreground mb-2">
          No posts yet
        </h3>
        <p className="text-muted-foreground text-center max-w-sm mb-6">
          There are no posts to display at the moment. Be the first to share
          something with the community!
        </p>
        <div className="flex gap-2 text-sm text-muted-foreground">
          <span className="inline-flex items-center">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-4 w-4 mr-1"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            Check back later for updates
          </span>
        </div>
      </CardContent>
    </Card>
  );
}

function Feed() {
  const [posts, setPosts] = useState<Post[]>([]);

  useEffect(() => {
    const fetchPosts = async () => {
      try {
        // FIXME: use axios or similar with proper base URL configuration and
        // error handling as well as types
        const response = await fetch("http://localhost/content/posts");
        if (!response.ok) {
          throw new Error("Failed to fetch posts");
        }
        const data = await response.json();
        setPosts(data);
      } catch (error) {
        console.error("Error fetching posts:", error);
      }
    };
    fetchPosts();
  }, []);

  if (!posts || posts.length === 0) {
    return (
      <>
        <div className="mb-6">
          <FloatingActionButton />
        </div>
        <EmptyFeedState />
      </>
    );
  }

  return (
    <div className="space-y-4">
      <div className="mb-6">
        <FloatingActionButton />
      </div>
      {posts.map((post) => (
        <PostContainer key={post.id} post={post} />
      ))}
    </div>
  );
}

export default Feed;
