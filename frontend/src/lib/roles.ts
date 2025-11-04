/**
 * Role-based access control types and utilities
 */

export type UserRole = "student" | "admin";

export const ROLES = {
  STUDENT: "student" as UserRole,
  ADMIN: "admin" as UserRole,
};

/**
 * Check if a role is admin
 */
export const isAdmin = (role?: UserRole): boolean => {
  return role === ROLES.ADMIN;
};

/**
 * Check if a role is student
 */
export const isStudent = (role?: UserRole): boolean => {
  return role === ROLES.STUDENT;
};

/**
 * Check if a user has one of the allowed roles
 */
export const hasRole = (
  userRole?: UserRole,
  allowedRoles?: UserRole[]
): boolean => {
  if (!allowedRoles || allowedRoles.length === 0) {
    return true; // No role restriction
  }
  if (!userRole) {
    return false;
  }
  return allowedRoles.includes(userRole);
};

/**
 * Get role display name
 */
export const getRoleDisplayName = (role: UserRole): string => {
  switch (role) {
    case ROLES.ADMIN:
      return "Admin";
    case ROLES.STUDENT:
      return "Student";
    default:
      return "Unknown";
  }
};
