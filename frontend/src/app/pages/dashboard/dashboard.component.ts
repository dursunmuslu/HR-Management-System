import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { AuthService } from '../../core/services/auth.service';

export interface CompanyModuleSettings {
  is_announcements_enabled: boolean;
  is_quizzes_enabled: boolean;
  is_shifts_enabled: boolean;
  is_leaves_enabled: boolean;
  is_timesheets_enabled: boolean;
}

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss'
})
export class DashboardComponent implements OnInit {
  private authService = inject(AuthService);
  private http = inject(HttpClient);

  readonly baseApi = 'https://hr-management-api-6rpx.onrender.com';

  isLoading = true;
  user: any = null;

  // Modül Ayarları
  moduleSettings: CompanyModuleSettings = {
    is_announcements_enabled: true,
    is_quizzes_enabled: true,
    is_shifts_enabled: true,
    is_leaves_enabled: true,
    is_timesheets_enabled: true
  };

  // İstatistik & Veriler
  stats = {
    totalEmployees: 0,
    activeEmployees: 0,
    pendingLeaves: 0,
    remainingLeaveDays: 14,
    pinnedAnnouncement: null as any,
    nextShift: null as any,
    totalMissingMinutes: 0,
    totalOvertimeMinutes: 0,
    averageSurveyScore: 0,
    targetSurveyScore: 85
  };

  get isManager(): boolean {
    const role = this.user?.role;
    return role === 'YONETICI' || role === 'PLATFORM_OWNER';
  }

  get isTeamLeader(): boolean {
    return this.user?.role === 'TAKIM_LIDERI';
  }

  get isEmployee(): boolean {
    return this.user?.role === 'PERSONEL';
  }

  // Modül görünürlük kuralları
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

  ngOnInit(): void {
    this.user = this.authService.getStoredUser();
    this.loadSettings();
    this.loadDashboardData();
  }

  loadSettings(): void {
    this.http.get<CompanyModuleSettings>(`${this.baseApi}/companies/my-settings`).subscribe({
      next: (res) => {
        if (res) {
          this.moduleSettings = { ...this.moduleSettings, ...res };
        }
      },
      error: () => {}
    });
  }

  loadDashboardData(): void {
    this.isLoading = true;

    // 1. Yönetici için Genel İstatistikler
    if (this.isManager) {
      this.http.get<any[]>(`${this.baseApi}/employees/`).subscribe({
        next: (emps) => {
          if (Array.isArray(emps)) {
            this.stats.totalEmployees = emps.length;
            this.stats.activeEmployees = emps.filter(e => e.is_active !== false).length;
          }
        },
        error: () => {}
      });

      this.http.get<any[]>(`${this.baseApi}/leaves/pending`).subscribe({
        next: (leaves) => {
          if (Array.isArray(leaves)) {
            this.stats.pendingLeaves = leaves.length;
          }
        },
        error: () => {}
      });
    }

    // 2. Sabitlenmiş veya Son Duyuru
    this.http.get<any[]>(`${this.baseApi}/announcements/`).subscribe({
      next: (anns) => {
        if (Array.isArray(anns) && anns.length > 0) {
          this.stats.pinnedAnnouncement = anns.find(a => a.is_pinned) || anns[0];
        }
      },
      error: () => {}
    });

    // 3. Puantaj ve Anket Verileri
    const tsEndpoint = this.isManager ? '/timesheets/company-records' : '/timesheets/my-records';
    this.http.get<any>(`${this.baseApi}${tsEndpoint}`).subscribe({
      next: (res) => {
        const timesheets = res?.timesheets || [];
        const surveys = res?.surveys || [];

        // Eksik ve fazla mesai
        this.stats.totalMissingMinutes = timesheets
          .filter((t: any) => t.diff_minutes < 0)
          .reduce((acc: number, curr: any) => acc + Math.abs(curr.diff_minutes), 0);

        this.stats.totalOvertimeMinutes = timesheets
          .filter((t: any) => t.diff_minutes > 0)
          .reduce((acc: number, curr: any) => acc + curr.diff_minutes, 0);

        // Anket puanı ortalaması
        if (surveys.length > 0) {
          const total = surveys.reduce((acc: number, s: any) => acc + (s.actual_score || 0), 0);
          this.stats.averageSurveyScore = +(total / surveys.length).toFixed(1);
          this.stats.targetSurveyScore = surveys[0]?.target_score || 85;
        }

        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
      }
    });

    // 4. Günlük Vardiya Bilgisi
    this.http.get<any>(`${this.baseApi}/shifts/daily`).subscribe({
      next: (shift) => {
        if (shift) {
          this.stats.nextShift = shift;
        }
      },
      error: () => {}
    });
  }

  formatMinutes(min: number): string {
    const abs = Math.abs(min);
    const h = Math.floor(abs / 60);
    const m = abs % 60;
    return `${h > 0 ? h + 's ' : ''}${m} dk`;
  }
}
