import { BrowserRouter, Routes, Route } from "react-router-dom";
import { useState } from "react";
import { Layout } from "./components/Layout";
import { AuthProvider } from "./contexts/AuthContext";
import { ProtectedRoute } from "./components/ProtectedRoute";
import WIP from "./pages/WIP";
import Login from "./pages/Login";
import Register from "./pages/Register";
import UploadDocument from "./pages/UploadDocument";
import Materials from "./pages/Materials";

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
              <ProtectedRoute>
                <Layout layoutProps={layoutProps}>
                  <Routes>
                    <Route path="/" element={<Materials />} />
                    <Route path="/courses" element={<WIP />} />
                    <Route path="/profile" element={<WIP />} />
                    <Route path="/settings" element={<WIP />} />
                    <Route
                      path="/upload/document"
                      element={<UploadDocument />}
                    />
                  </Routes>
                </Layout>
              </ProtectedRoute>
            }
          />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
