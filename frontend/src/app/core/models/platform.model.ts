export interface PlatformSummary {
  total_companies: number;
  active_companies: number;
  suspended_companies: number;

  total_users: number;
  total_managers: number;
  total_employees: number;
}


export interface PlatformCompany {
  id: number;

  code: string;
  name: string;

  is_active: boolean;

  user_count: number;
  manager_count: number;
  employee_count: number;

  created_at: string;

  suspended_at?: string | null;
  suspension_reason?: string | null;
}


export interface InitialCompanyAdminRequest {
  username: string;
  temporary_password: string;
}


export interface CreateCompanyWithAdminRequest {
  name: string;
  code: string;

  tax_number?: string | null;
  address?: string | null;

  admin: InitialCompanyAdminRequest;
}


export interface CompanyCreationResponse {
  company_id: number;
  company_name: string;
  company_code: string;

  admin_user_id: number;
  admin_username: string;

  must_change_password: boolean;

  message: string;
}


export interface SuspendCompanyRequest {
  reason: string;
}


export interface CompanyStatusResponse {
  id: number;

  code: string;
  name: string;

  is_active: boolean;

  suspended_at: string | null;
  suspension_reason: string | null;
}
