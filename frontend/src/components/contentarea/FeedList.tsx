import { PostContainer } from "../post/PostContainer";

export function Feed() {
  // Mock data for posts
  const posts = [
    {
      id: 1,
      user: {
        name: "Emma Wilson",
        avatar: "https://randomuser.me/api/portraits/women/44.jpg",
      },
      date: new Date("2023-09-15T14:32:00"),
      content:
        "Just submitted my research paper on renewable energy sources. Would love to get some feedback from anyone interested in sustainability!",
      commentCount: 8,
      likes: 24,
    },
    {
      id: 2,
      user: {
        name: "Michael Chen",
        avatar: "https://randomuser.me/api/portraits/men/32.jpg",
      },
      date: new Date("2023-09-14T09:15:00"),
      content:
        "Here are my notes from today's calculus lecture. Hope they help! #math #calculus",
      commentCount: 12,
      likes: 45,
      image:
        "https://images.unsplash.com/photo-1621600411688-4be93c2c1208?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=880&q=80",
    },
    {
      id: 3,
      user: {
        name: "Sophia Rodriguez",
        avatar: "https://randomuser.me/api/portraits/women/68.jpg",
      },
      date: new Date("2023-09-13T16:45:00"),
      content:
        "Our team won the coding competition! So proud of everyone's hard work and dedication. Looking forward to the next challenge!",
      commentCount: 32,
      likes: 87,
    },
  ];

  return (
    <div className="space-y-4">
      {posts.map((post) => (
        <PostContainer key={post.id} post={post} />
      ))}
    </div>
  );
}

// Export as PostList for backward compatibility
export { Feed as PostList };
