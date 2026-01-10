/**
 * Authentication and User Types
 */

export type UserRole = 'admin' | 'manager' | 'staff' | 'customer';

export interface User {
  id: number;
  email: string;
  role: UserRole;
  name?: string;
  phone?: string;
  avatar?: string;
  created_at: string;
  updated_at: string;
}

export interface Profile {
  user: User;
  phone?: string;
  avatar?: string;
  timezone: string;
  preferences: Record<string, any>;
  calendar_sync_enabled: boolean;
  calendar_provider: 'google' | 'outlook' | 'apple' | 'none';
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  token: string | null;
  refreshToken: string | null;
}

export interface ManagerPermissions {
  can_manage_customers: boolean;
  can_manage_staff: boolean;
  can_manage_appointments: boolean;
  can_view_reports: boolean;
  managed_locations?: number[];
  managed_staff?: number[];
  managed_customers?: number[];
  can_manage_all: boolean;
}
