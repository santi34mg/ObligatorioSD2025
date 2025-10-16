import { useState } from "react";
import { Layout } from "./components/layout/Layout";

function App() {
  const [isChatOpen, setIsChatOpen] = useState(false);
  return (
    <Layout
      isChatOpen={isChatOpen}
      toggleChat={() => setIsChatOpen(!isChatOpen)}
    />
  );
}

export default App;
