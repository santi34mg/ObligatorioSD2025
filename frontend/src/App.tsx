import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ContentArea } from "./components/contentarea/ContentArea";
import { useState } from "react";
import { Layout } from "./components/Layout";
import { AuthProvider } from "./contexts/AuthContext";
import WIP from "./pages/WIP";
import Login from "./pages/Login";
import Register from "./pages/Register";

export default function App() {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const toggleChat = () => {
    setIsChatOpen(!isChatOpen);
  };
  const layoutProps = { isChatOpen, toggleChat };

  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/*"
            element={
              <Layout layoutProps={layoutProps}>
                <Routes>
                  <Route path="/" element={<ContentArea />} />
                  <Route path="/courses" element={<WIP />} />
                  <Route path="/profile" element={<WIP />} />
                  <Route path="/settings" element={<WIP />} />
                </Routes>
              </Layout>
            }
          />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
