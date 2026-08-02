export interface Company {
  id: number;
  name: string;
  tax_number?: string | null;
  address?: string | null;
  is_active: boolean;
}

export interface CreateCompanyRequest {
  name: string;
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
  company_id: number;
  name: string;
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
