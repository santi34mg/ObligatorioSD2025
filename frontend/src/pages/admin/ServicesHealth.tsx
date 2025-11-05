import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Activity,
  CheckCircle2,
  XCircle,
  RefreshCw,
  Loader2,
  Shield,
  ShieldOff,
  User,
} from "lucide-react";
import { toast } from "sonner";

type AuthLevel = "no-token" | "student" | "admin" | "invalid-token";
type ServiceStatus = "healthy" | "unhealthy" | "unknown" | "testing";

interface ServiceEndpoint {
  name: string;
  path: string;
  requiresAuth: boolean;
  adminOnly?: boolean;
}

interface ServiceHealth {
  name: string;
  endpoints: ServiceEndpoint[];
  baseUrl: string;
  status: {
    "no-token": ServiceStatus;
    student: ServiceStatus;
    admin: ServiceStatus;
    "invalid-token": ServiceStatus;
  };
  lastChecked?: Date;
}

const API_BASE_URL = "http://localhost/api";

// Define all services and their endpoints
const SERVICES: ServiceHealth[] = [
  {
    name: "Auth Service",
    baseUrl: `${API_BASE_URL}/auth`,
    endpoints: [
      { name: "Health Check", path: "/health", requiresAuth: false },
      { name: "Get Current User", path: "/me", requiresAuth: true },
    ],
    status: {
      "no-token": "unknown",
      student: "unknown",
      admin: "unknown",
      "invalid-token": "unknown",
    },
  },
  {
    name: "Users Service",
    baseUrl: `${API_BASE_URL}/users`,
    endpoints: [
      { name: "Health Check", path: "/health", requiresAuth: false },
      {
        name: "List Users",
        path: "/list",
        requiresAuth: true,
        adminOnly: true,
      },
    ],
    status: {
      "no-token": "unknown",
      student: "unknown",
      admin: "unknown",
      "invalid-token": "unknown",
    },
  },
  {
    name: "Friendship Service",
    baseUrl: `${API_BASE_URL}/friendships`,
    endpoints: [
      { name: "Health Check", path: "/health", requiresAuth: false },
      { name: "Get Friends", path: "/", requiresAuth: true },
    ],
    status: {
      "no-token": "unknown",
      student: "unknown",
      admin: "unknown",
      "invalid-token": "unknown",
    },
  },
  {
    name: "Content Service",
    baseUrl: `${API_BASE_URL}/content`,
    endpoints: [
      { name: "Health Check", path: "/health", requiresAuth: false },
      { name: "List Content", path: "/documents", requiresAuth: true },
    ],
    status: {
      "no-token": "unknown",
      student: "unknown",
      admin: "unknown",
      "invalid-token": "unknown",
    },
  },
  {
    name: "Communication Service",
    baseUrl: `${API_BASE_URL}/communication`,
    endpoints: [
      { name: "Health Check", path: "/health", requiresAuth: false },
      { name: "Get Messages", path: "/messages", requiresAuth: true },
    ],
    status: {
      "no-token": "unknown",
      student: "unknown",
      admin: "unknown",
      "invalid-token": "unknown",
    },
  },
  {
    name: "Collaboration Service",
    baseUrl: `${API_BASE_URL}/collab`,
    endpoints: [
      { name: "Health Check", path: "/health", requiresAuth: false },
      { name: "Get Sessions", path: "/sessions", requiresAuth: true },
    ],
    status: {
      "no-token": "unknown",
      student: "unknown",
      admin: "unknown",
      "invalid-token": "unknown",
    },
  },
  {
    name: "WebSocket Service",
    baseUrl: `${API_BASE_URL}/ws`,
    endpoints: [{ name: "Health Check", path: "/health", requiresAuth: false }],
    status: {
      "no-token": "unknown",
      student: "unknown",
      admin: "unknown",
      "invalid-token": "unknown",
    },
  },
  {
    name: "Moderation Service",
    baseUrl: `${API_BASE_URL}/moderation`,
    endpoints: [{ name: "Health Check", path: "/health", requiresAuth: false }],
    status: {
      "no-token": "unknown",
      student: "unknown",
      admin: "unknown",
      "invalid-token": "unknown",
    },
  },
];

export default function ServicesHealth() {
  const [services, setServices] = useState<ServiceHealth[]>(SERVICES);
  const [isChecking, setIsChecking] = useState(false);
  const [selectedAuth, setSelectedAuth] = useState<AuthLevel>("admin");

  // Get tokens from localStorage
  const getToken = (level: AuthLevel): string | null => {
    switch (level) {
      case "admin":
        return localStorage.getItem("access_token");
      case "student":
        return (
          localStorage.getItem("student_token") ||
          localStorage.getItem("access_token")
        );
      case "invalid-token":
        return "invalid-token-12345";
      case "no-token":
      default:
        return null;
    }
  };

  // Check a single service with a specific auth level
  const checkService = async (
    service: ServiceHealth,
    authLevel: AuthLevel
  ): Promise<ServiceStatus> => {
    const token = getToken(authLevel);

    // Test the main endpoint or first available endpoint
    const testEndpoint = service.endpoints[0];
    const url = `${service.baseUrl}${testEndpoint.path}`;

    try {
      const headers: HeadersInit = {
        "Content-Type": "application/json",
      };

      if (token && testEndpoint.requiresAuth) {
        headers["Authorization"] = `Bearer ${token}`;
      }

      const response = await fetch(url, {
        method: "GET",
        headers,
      });

      // Consider these statuses as healthy
      if (response.ok) {
        return "healthy";
      }

      // 401/403 with auth means service is up but denying access (still healthy)
      if (
        (response.status === 401 || response.status === 403) &&
        testEndpoint.requiresAuth
      ) {
        // If we're testing with no token or invalid token and getting 401, that's expected
        if (authLevel === "no-token" || authLevel === "invalid-token") {
          return "healthy"; // Service correctly rejecting
        }
        // If we have a token but getting 403, could be permission issue
        if (authLevel === "student" && testEndpoint.adminOnly) {
          return "healthy"; // Expected behavior
        }
        return "unhealthy"; // Unexpected auth failure
      }

      return "unhealthy";
    } catch (error) {
      console.error(`Error checking ${service.name}:`, error);
      return "unhealthy";
    }
  };

  // Check all services with all auth levels
  const checkAllServices = async () => {
    setIsChecking(true);

    try {
      const updatedServices = await Promise.all(
        services.map(async (service) => {
          const statuses = await Promise.all([
            checkService(service, "no-token"),
            checkService(service, "student"),
            checkService(service, "admin"),
            checkService(service, "invalid-token"),
          ]);

          return {
            ...service,
            status: {
              "no-token": statuses[0],
              student: statuses[1],
              admin: statuses[2],
              "invalid-token": statuses[3],
            },
            lastChecked: new Date(),
          };
        })
      );

      setServices(updatedServices);

      toast.success("Health check complete - All services have been tested");
    } catch (error) {
      toast.error("Failed to complete health checks");
    } finally {
      setIsChecking(false);
    }
  };

  // Check services on mount
  useEffect(() => {
    checkAllServices();
  }, []);

  const getStatusIcon = (status: ServiceStatus) => {
    switch (status) {
      case "healthy":
        return <CheckCircle2 className="h-5 w-5 text-green-500" />;
      case "unhealthy":
        return <XCircle className="h-5 w-5 text-red-500" />;
      case "testing":
        return <Loader2 className="h-5 w-5 animate-spin text-blue-500" />;
      default:
        return <Activity className="h-5 w-5 text-gray-400" />;
    }
  };

  const getStatusBadge = (status: ServiceStatus) => {
    switch (status) {
      case "healthy":
        return <Badge className="bg-green-500">Healthy</Badge>;
      case "unhealthy":
        return <Badge variant="destructive">Unhealthy</Badge>;
      case "testing":
        return <Badge className="bg-blue-500">Testing</Badge>;
      default:
        return <Badge variant="outline">Unknown</Badge>;
    }
  };

  const getAuthLevelIcon = (level: AuthLevel) => {
    switch (level) {
      case "admin":
        return <Shield className="h-4 w-4" />;
      case "student":
        return <User className="h-4 w-4" />;
      case "no-token":
        return <ShieldOff className="h-4 w-4" />;
      case "invalid-token":
        return <XCircle className="h-4 w-4" />;
    }
  };

  const getAuthLevelLabel = (level: AuthLevel) => {
    switch (level) {
      case "admin":
        return "Admin Token";
      case "student":
        return "Student Token";
      case "no-token":
        return "No Token";
      case "invalid-token":
        return "Invalid Token";
    }
  };

  // Calculate overall health
  const overallHealthy = services.filter(
    (s) => s.status[selectedAuth] === "healthy"
  ).length;
  const overallUnhealthy = services.filter(
    (s) => s.status[selectedAuth] === "unhealthy"
  ).length;

  return (
    <div className="h-full overflow-y-auto">
      <div className="container mx-auto p-6 pb-12">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold mb-2">Services Health Monitor</h1>
          <p className="text-gray-600">
            Monitor the health status of all microservices and test
            authorization levels
          </p>
        </div>
        {/* Controls */}
        <div className="mb-6 flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
          <div className="flex flex-wrap gap-2">
            {(
              ["no-token", "student", "admin", "invalid-token"] as AuthLevel[]
            ).map((level) => (
              <Button
                key={level}
                variant={selectedAuth === level ? "default" : "outline"}
                size="sm"
                onClick={() => setSelectedAuth(level)}
                className="flex items-center gap-2"
              >
                {getAuthLevelIcon(level)}
                {getAuthLevelLabel(level)}
              </Button>
            ))}
          </div>

          <Button
            onClick={checkAllServices}
            disabled={isChecking}
            className="flex items-center gap-2"
          >
            {isChecking ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Checking...
              </>
            ) : (
              <>
                <RefreshCw className="h-4 w-4" />
                Refresh All
              </>
            )}
          </Button>
        </div>
        {/* Overall Status */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5" />
              Overall Status ({getAuthLevelLabel(selectedAuth)})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex gap-6 items-center">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5 text-green-500" />
                <span className="text-2xl font-bold">{overallHealthy}</span>
                <span className="text-gray-600">Healthy</span>
              </div>
              <div className="flex items-center gap-2">
                <XCircle className="h-5 w-5 text-red-500" />
                <span className="text-2xl font-bold">{overallUnhealthy}</span>
                <span className="text-gray-600">Unhealthy</span>
              </div>
              <div className="flex items-center gap-2">
                <Activity className="h-5 w-5 text-gray-400" />
                <span className="text-2xl font-bold">
                  {services.length - overallHealthy - overallUnhealthy}
                </span>
                <span className="text-gray-600">Unknown</span>
              </div>
            </div>
          </CardContent>
        </Card>
        {/* Services Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
          {services.map((service) => (
            <Card
              key={service.name}
              className="hover:shadow-lg transition-shadow"
            >
              <CardHeader>
                <div className="flex items-start justify-between">
                  <CardTitle className="text-lg">{service.name}</CardTitle>
                  {getStatusIcon(service.status[selectedAuth])}
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {/* Current auth level status */}
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">
                      {getAuthLevelLabel(selectedAuth)}:
                    </span>
                    {getStatusBadge(service.status[selectedAuth])}
                  </div>

                  {/* All auth levels status */}
                  <div className="border-t pt-3 space-y-2">
                    <p className="text-xs font-semibold text-gray-500 mb-2">
                      All Authorization Levels:
                    </p>
                    {(
                      [
                        "no-token",
                        "invalid-token",
                        "student",
                        "admin",
                      ] as AuthLevel[]
                    ).map((level) => (
                      <div
                        key={level}
                        className="flex items-center justify-between text-xs"
                      >
                        <span className="flex items-center gap-1">
                          {getAuthLevelIcon(level)}
                          {getAuthLevelLabel(level)}
                        </span>
                        {getStatusIcon(service.status[level])}
                      </div>
                    ))}
                  </div>

                  {/* Endpoints */}
                  <div className="border-t pt-3">
                    <p className="text-xs font-semibold text-gray-500 mb-2">
                      Test Endpoints:
                    </p>
                    {service.endpoints.map((endpoint, idx) => (
                      <div key={idx} className="text-xs text-gray-600 mb-1">
                        <span className="font-mono">{endpoint.path}</span>
                        {endpoint.requiresAuth && (
                          <Badge variant="outline" className="ml-2 text-xs">
                            {endpoint.adminOnly ? "Admin" : "Auth"}
                          </Badge>
                        )}
                      </div>
                    ))}
                  </div>

                  {/* Last checked */}
                  {service.lastChecked && (
                    <div className="text-xs text-gray-500 border-t pt-2">
                      Last checked: {service.lastChecked.toLocaleTimeString()}
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Legend */}
        <Card className="mt-6 mb-8">
          <CardHeader>
            <CardTitle className="text-lg">
              Authorization Levels Explained
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <ShieldOff className="h-4 w-4" />
                  <strong>No Token:</strong>
                </div>
                <p className="text-gray-600 ml-6">
                  Requests without authentication. Should work for public
                  endpoints only.
                </p>
              </div>
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <XCircle className="h-4 w-4" />
                  <strong>Invalid Token:</strong>
                </div>
                <p className="text-gray-600 ml-6">
                  Requests with an invalid/malformed token. Should be rejected
                  by all protected endpoints.
                </p>
              </div>
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <User className="h-4 w-4" />
                  <strong>Student Token:</strong>
                </div>
                <p className="text-gray-600 ml-6">
                  Regular user authentication. Has access to user-level
                  endpoints.
                </p>
              </div>
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <Shield className="h-4 w-4" />
                  <strong>Admin Token:</strong>
                </div>
                <p className="text-gray-600 ml-6">
                  Administrator authentication. Has access to all endpoints
                  including admin-only features.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
