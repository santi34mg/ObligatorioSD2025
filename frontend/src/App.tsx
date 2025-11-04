import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Layout } from "./components/Layout";
import { AuthProvider } from "./contexts/AuthContext";
import { ToastProvider } from "./contexts/ToastContext";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { Toaster } from "./components/ui/sonner";
import { ROLES } from "./lib/roles";
import WIP from "./pages/WIP";
import Login from "./pages/Login";
import Register from "./pages/Register";
import UploadDocument from "./pages/UploadDocument";
import Materials from "./pages/Materials";
import Connections from "./pages/Connections";
import AdminPanel from "./pages/admin/AdminPanel";
import UserManagement from "./pages/admin/UserManagement";

export default function App() {
  return (
    <AuthProvider>
      <ToastProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route
              path="/*"
              element={
                <ProtectedRoute>
                  <Layout>
                    <Routes>
                      <Route path="/" element={<Materials />} />
                      <Route path="/connections" element={<Connections />} />
                      <Route
                        path="/upload/document"
                        element={<UploadDocument />}
                      />
                      {/* Admin Routes - Only accessible to admins */}
                      <Route
                        path="/admin"
                        element={
                          <ProtectedRoute allowedRoles={[ROLES.ADMIN]}>
                            <AdminPanel />
                          </ProtectedRoute>
                        }
                      />
                      <Route
                        path="/admin/users"
                        element={
                          <ProtectedRoute allowedRoles={[ROLES.ADMIN]}>
                            <UserManagement />
                          </ProtectedRoute>
                        }
                      />
                      {/* Rest of the routes are WIP */}
                      <Route path="/*" element={<WIP />} />
                    </Routes>
                    <Toaster />
                  </Layout>
                </ProtectedRoute>
              }
            />
          </Routes>
        </BrowserRouter>
      </ToastProvider>
    </AuthProvider>
  );
}
