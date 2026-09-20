import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';

export interface CompanyModuleSettings {
  is_announcements_enabled: boolean;
  is_quizzes_enabled: boolean;
  is_shifts_enabled: boolean;
  is_leaves_enabled: boolean;
  is_timesheets_enabled: boolean;
}

@Component({
  selector: 'app-main-layout',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink,
    RouterLinkActive,
    RouterOutlet
  ],
  templateUrl: './main-layout.component.html',
  styleUrl: './main-layout.component.scss'
})
export class MainLayoutComponent implements OnInit {
  private readonly authService = inject(AuthService);
  private readonly http = inject(HttpClient);

  readonly settingsApiUrl = 'https://hr-management-api-6rpx.onrender.com/companies/my-settings';

  sidebarOpen = false;

  moduleSettings: CompanyModuleSettings = {
    is_announcements_enabled: true,
    is_quizzes_enabled: true,
    is_shifts_enabled: true,
    is_leaves_enabled: true,
    is_timesheets_enabled: true
  };

  ngOnInit(): void {
    this.loadSettings();
  }

  loadSettings(): void {
    this.http.get<CompanyModuleSettings>(this.settingsApiUrl).subscribe({
      next: (settings: any) => {
        if (settings) {
          this.moduleSettings = {
            is_announcements_enabled: settings.is_announcements_enabled ?? true,
            is_quizzes_enabled: settings.is_quizzes_enabled ?? true,
            is_shifts_enabled: settings.is_shifts_enabled ?? true,
            is_leaves_enabled: settings.is_leaves_enabled ?? true,
            is_timesheets_enabled: settings.is_timesheets_enabled ?? true
          };
          // LocalStorage'ı da senkronize et ki guardlar engellemesin
          localStorage.setItem('cfg_show_quizzes', String(this.moduleSettings.is_quizzes_enabled));
          localStorage.setItem('cfg_show_shifts', String(this.moduleSettings.is_shifts_enabled));
          localStorage.setItem('cfg_show_announcements', String(this.moduleSettings.is_announcements_enabled));
          localStorage.setItem('cfg_show_timesheets', String(this.moduleSettings.is_timesheets_enabled));
        }
      },
      error: () => {
        // Backend dönmezse bile ekranda her şey açık kalsın
      }
    });
  }

  get currentUser() {
    return this.authService.getStoredUser();
  }

  get isPlatformOwner(): boolean {
    const role = String(this.currentUser?.role || '').toUpperCase();
    return role === 'PLATFORM_OWNER';
  }

  get isManager(): boolean {
    const role = String(this.currentUser?.role || '').toUpperCase();
    return role === 'YONETICI' || role === 'PLATFORM_OWNER' || role === 'MANAGER';
  }

  get isTeamLeader(): boolean {
    const role = String(this.currentUser?.role || '').toUpperCase();
    return role === 'TAKIM_LIDERI' || role === 'TEAM_LEADER';
  }

  get isEmployee(): boolean {
    const role = String(this.currentUser?.role || '').toUpperCase();
    return role === 'PERSONEL' || role === 'EMPLOYEE';
  }

  // YÖNETİCİ HER ZAMAN GÖRÜR; PERSONEL AYAR AÇIKSA GÖRÜR
  get showAnnouncements(): boolean {
    return this.isManager || this.moduleSettings.is_announcements_enabled !== false;
  }

  get showQuizzes(): boolean {
    return this.isManager || this.moduleSettings.is_quizzes_enabled !== false;
  }

  get showShifts(): boolean {
    return this.isManager || this.moduleSettings.is_shifts_enabled !== false;
  }

  get showTimesheets(): boolean {
    return this.isManager || this.moduleSettings.is_timesheets_enabled !== false;
  }

  get showLeaves(): boolean {
    return this.isManager || this.moduleSettings.is_leaves_enabled !== false;
  }

  get homeRoute(): string {
    return this.isPlatformOwner ? '/platform' : '/dashboard';
  }

  get displayName(): string {
    return this.currentUser?.username || 'Kullanıcı';
  }

  get roleLabel(): string {
    if (this.isPlatformOwner) return 'Sistem Sahibi';
    if (this.isManager) return 'Şirket Yöneticisi';
    if (this.isTeamLeader) return 'Takım Lideri';
    if (this.isEmployee) return 'Personel';
    return 'Kullanıcı';
  }

  get applicationTitle(): string {
    return this.isPlatformOwner ? 'HR Platform Yönetimi' : 'İnsan Kaynakları Yönetim Sistemi';
  }

  get applicationDescription(): string {
    return this.isPlatformOwner
      ? 'Şirketleri ve platform erişimlerini yönetin'
      : 'Personel ve izin süreçlerinizi yönetin';
  }

  get userInitial(): string {
    return this.displayName.charAt(0).toLocaleUpperCase('tr-TR');
  }

  toggleSidebar(): void {
    this.sidebarOpen = !this.sidebarOpen;
  }

  closeSidebar(): void {
    this.sidebarOpen = false;
  }

  logout(): void {
    this.authService.logout();
  }
}
