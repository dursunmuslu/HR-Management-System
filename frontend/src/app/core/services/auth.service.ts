import { HttpClient } from '@angular/common/http';
import {
  Injectable,
  PLATFORM_ID,
  inject
} from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { Router } from '@angular/router';
import {
  Observable,
  tap
} from 'rxjs';

import { environment } from '../../../environments/environment';
import {
  CurrentUser,
  LoginRequest,
  TokenResponse
} from '../models/auth.model';

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  private readonly http = inject(HttpClient);
  private readonly router = inject(Router);
  private readonly platformId = inject(PLATFORM_ID);

  private readonly apiUrl = environment.apiUrl;
  private readonly tokenKey = 'hr_access_token';
  private readonly userKey = 'hr_current_user';

  private get isBrowser(): boolean {
    return isPlatformBrowser(this.platformId);
  }

  login(request: LoginRequest): Observable<TokenResponse> {
    return this.http.post<TokenResponse>(
      `${this.apiUrl}/auth/login`,
      request
    ).pipe(
      tap(response => {
        this.setToken(response.access_token);
      })
    );
  }

  getCurrentUser(): Observable<CurrentUser> {
    return this.http.get<CurrentUser>(
      `${this.apiUrl}/auth/me`
    ).pipe(
      tap(user => {
        this.setStoredUser(user);
      })
    );
  }

  setToken(token: string): void {
    if (!this.isBrowser) {
      return;
    }

    localStorage.setItem(
      this.tokenKey,
      token
    );
  }

  getToken(): string | null {
    if (!this.isBrowser) {
      return null;
    }

    return localStorage.getItem(
      this.tokenKey
    );
  }

  setStoredUser(user: CurrentUser): void {
    if (!this.isBrowser) {
      return;
    }

    localStorage.setItem(
      this.userKey,
      JSON.stringify(user)
    );
  }

  getStoredUser(): CurrentUser | null {
    if (!this.isBrowser) {
      return null;
    }

    const storedUser = localStorage.getItem(
      this.userKey
    );

    if (!storedUser) {
      return null;
    }

    try {
      return JSON.parse(storedUser) as CurrentUser;
    } catch {
      localStorage.removeItem(this.userKey);
      return null;
    }
  }

  isAuthenticated(): boolean {
    return Boolean(this.getToken());
  }

  isManager(): boolean {
    return this.getStoredUser()?.role === 'YONETICI';
  }

  logout(): void {
    if (this.isBrowser) {
      localStorage.removeItem(this.tokenKey);
      localStorage.removeItem(this.userKey);
    }

    void this.router.navigate(['/login']);
  }
}
