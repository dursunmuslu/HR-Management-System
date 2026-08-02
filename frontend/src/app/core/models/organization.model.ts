export interface Company {
  id: number;
  code: string;
  name: string;

  tax_number?: string | null;
  address?: string | null;

  is_active: boolean;

  suspended_at?: string | null;
  suspension_reason?: string | null;

  created_at: string;
  updated_at: string;
}

export interface UpdateCompanyRequest {
  name?: string;
  tax_number?: string | null;
  address?: string | null;
}

export interface Department {
  id: number;
  company_id: number;

  name: string;
  description?: string | null;

  is_active: boolean;
}

export interface CreateDepartmentRequest {
  name: string;
  description?: string | null;
}

export interface UpdateDepartmentRequest {
  name?: string;
  description?: string | null;
}

export interface Team {
  id: number;
  department_id: number;

  name: string;
  description?: string | null;

  is_active: boolean;
}

export interface CreateTeamRequest {
  department_id: number;
  name: string;
  description?: string | null;
}

export interface UpdateTeamRequest {
  name?: string;
  description?: string | null;
}
