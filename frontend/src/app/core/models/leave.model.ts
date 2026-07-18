export type LeaveStatus =
  | 'PENDING'
  | 'APPROVED'
  | 'REJECTED'
  | 'CANCELLED';

export type LeaveType =
  | 'YILLIK_IZIN'
  | 'HASTALIK_IZNI'
  | 'MAZERET_IZNI'
  | 'UCRETSIZ_IZIN';

export interface LeaveEmployee {
  id: number;
  first_name: string;
  last_name: string;
  employee_number: string;
  department: string;
  position: string;
}

export interface LeaveRequest {
  id: number;
  employee_id: number;

  leave_type: LeaveType;
  start_date: string;
  end_date: string;

  number_of_days: number;
  description: string | null;

  status: LeaveStatus;
  manager_note: string | null;
  created_at: string;

  /*
   * Yönetici izin listesindeki detay endpointleri
   * employee nesnesini de döndürüyor.
   *
   * Personelin kendi izin listesinde bu alan gelmeyebilir.
   */
  employee?: LeaveEmployee;
}

export interface CreateLeaveRequest {
  leave_type: LeaveType;
  start_date: string;
  end_date: string;
  description?: string | null;
}

export interface LeaveBalance {
  employee_id: number;
  employee_number: string;
  first_name: string;
  last_name: string;
  remaining_annual_leave: number;
}

export interface LeaveActionRequest {
  manager_note?: string | null;
}
