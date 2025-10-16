import { PostList } from "../post/PostList";
export function ContentArea() {
  return (
    <div className="max-w-2xl mx-auto py-6 px-4 h-full overflow-y-auto">
      <h2 className="text-2xl font-bold mb-6">Recent Posts</h2>
      <PostList />
    </div>
  );
}
