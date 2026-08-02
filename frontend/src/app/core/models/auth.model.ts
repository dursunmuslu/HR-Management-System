export type UserRole =
  | 'PLATFORM_OWNER'
  | 'YONETICI'
  | 'PERSONEL';


export interface LoginRequest {
  username: string;
  password: string;
}


export interface CurrentUser {
  id: number;
  company_id: number | null;

  username: string;
  role: UserRole;

  is_active: boolean;
  must_change_password: boolean;

  password_changed_at?: string | null;
  last_login_at?: string | null;
  created_at?: string | null;
}


export interface TokenResponse {
  access_token: string;
  token_type: string;

  must_change_password: boolean;

  user: CurrentUser;
}


export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
  new_password_confirmation: string;
}
