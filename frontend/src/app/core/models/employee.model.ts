export type EmployeeRole =
  | 'PERSONEL'
  | 'YONETICI';

export interface EmployeeUser {
  id: number;
  username: string;
  role: EmployeeRole;
}

export interface Employee {
  id: number;
  user_id: number;

  first_name: string;
  last_name: string;
  tc_no: string;
  employee_number: string;
  department: string;
  position: string;
  phone: string;
  email: string;
  hire_date: string;
  remaining_annual_leave: number;

  /*
   * Backend nested user döndürürse kullanılır.
   */
  user?: EmployeeUser | null;

  /*
   * Eski veya düz response yapısıyla uyumluluk için.
   */
  username?: string | null;
  full_name?: string | null;
  role?: EmployeeRole | null;
  is_active?: boolean;
}

export interface CreateEmployeeRequest {
  username: string;
  password: string;
  first_name: string;
  last_name: string;
  tc_no: string;
  employee_number: string;
  department: string;
  position: string;
  phone: string;
  email: string;
  hire_date: string;
  remaining_annual_leave: number;
}

export interface UpdateEmployeeRequest {
  first_name?: string;
  last_name?: string;
  tc_no?: string;
  employee_number?: string;
  department?: string;
  position?: string;
  phone?: string;
  email?: string;
  hire_date?: string;
  remaining_annual_leave?: number;
}

export interface UpdateUserRoleRequest {
  role: EmployeeRole;
}

export interface UpdateUserRoleResponse {
  id: number;
  username: string;
  role: EmployeeRole;
}
