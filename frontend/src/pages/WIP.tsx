import { Card } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { useNavigate } from "react-router-dom";

export default function WIP() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen w-full bg-background">
      <main className="w-full flex items-center justify-center px-4 py-16">
        <Card className="max-w-md w-full p-8 text-center space-y-6">
          <div className="space-y-2">
            <div className="text-6xl mb-4">🚧</div>
            <h1 className="text-3xl font-bold">Work in Progress</h1>
            <p className="text-muted-foreground text-lg">
              This feature is currently under construction and will be added
              soon!
            </p>
          </div>
          <div className="pt-4">
            <Button onClick={() => navigate("/")} className="w-full" size="lg">
              Back to Home
            </Button>
          </div>
          <p className="text-sm text-muted-foreground">
            We're working hard to bring you new features. Stay tuned! ✨
          </p>
        </Card>
      </main>
    </div>
  );
}
