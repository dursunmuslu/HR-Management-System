export type EmployeeRole =
  | 'PERSONEL'
  | 'YONETICI'
  | 'PLATFORM_OWNER';


export interface EmployeeUser {
  id: number;
  company_id: number | null;

  username: string;
  role: EmployeeRole;

  is_active: boolean;
  must_change_password: boolean;

  password_changed_at?: string | null;
  last_login_at?: string | null;
  created_at?: string | null;
}


export interface EmployeeDepartment {
  id: number;
  company_id: number;

  name: string;
  is_active: boolean;
}


export interface EmployeeTeam {
  id: number;
  department_id: number;

  name: string;
  is_active: boolean;

  department: EmployeeDepartment;
}


export interface Employee {
  id: number;
  user_id: number;
  team_id: number | null;

  first_name: string;
  last_name: string;

  tc_no: string;
  employee_number: string;

  /**
   * Backend geçiş döneminde bu alanı
   * dönmeye devam ediyor.
   */
  department: string;

  position: string;
  phone: string;
  email: string;

  hire_date: string;
  remaining_annual_leave: number;

  user?: EmployeeUser | null;
  team?: EmployeeTeam | null;

  /**
   * Liste ekranlarının mevcut düz yapısıyla
   * geriye dönük uyumluluk.
   */
  username?: string | null;
  full_name?: string | null;
  role?: EmployeeRole | null;
  is_active?: boolean;
  must_change_password?: boolean;
}


export interface CreateEmployeeRequest {
  username: string;
  temporary_password: string;
  team_id: number;

  first_name: string;
  last_name: string;

  tc_no: string;
  employee_number: string;

  position: string;
  phone: string;
  email: string;

  hire_date: string;
  remaining_annual_leave: number;
}


export interface UpdateEmployeeRequest {
  team_id?: number;

  first_name?: string;
  last_name?: string;

  tc_no?: string;
  employee_number?: string;

  position?: string;
  phone?: string;
  email?: string;

  hire_date?: string;
  remaining_annual_leave?: number;
}


export interface UpdateUserRoleRequest {
  role: Exclude<
    EmployeeRole,
    'PLATFORM_OWNER'
  >;
}


export interface UpdateUserRoleResponse {
  id: number;
  company_id: number | null;

  username: string;
  role: EmployeeRole;

  is_active: boolean;
  must_change_password: boolean;
}
