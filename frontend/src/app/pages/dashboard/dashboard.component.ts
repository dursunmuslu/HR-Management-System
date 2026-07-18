import {
  CommonModule
} from '@angular/common';

import {
  HttpErrorResponse
} from '@angular/common/http';

import {
  Component,
  OnInit,
  inject
} from '@angular/core';

import {
  RouterLink
} from '@angular/router';

import {
  finalize
} from 'rxjs';

import {
  DashboardSummary
} from '../../core/models/dashboard.model';

import {
  LeaveBalance
} from '../../core/models/leave.model';

import {
  AuthService
} from '../../core/services/auth.service';

import {
  DashboardService
} from '../../core/services/dashboard.service';

import {
  LeaveService
} from '../../core/services/leave.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink
  ],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss'
})
export class DashboardComponent
  implements OnInit {

  private readonly dashboardService =
    inject(DashboardService);

  private readonly leaveService =
    inject(LeaveService);

  private readonly authService =
    inject(AuthService);

  readonly currentUser =
    this.authService.getStoredUser();

  summary:
    DashboardSummary | null = null;

  leaveBalance:
    LeaveBalance | null = null;

  isLoading = true;
  errorMessage = '';

  get isManager(): boolean {
    return (
      this.currentUser?.role ===
      'YONETICI'
    );
  }

  get isEmployee(): boolean {
    return (
      this.currentUser?.role ===
      'PERSONEL'
    );
  }

  get username(): string {
    return (
      this.currentUser?.username ??
      'Kullanıcı'
    );
  }

  get remainingAnnualLeave(): number {
    return (
      this.leaveBalance
        ?.remaining_annual_leave ??
      0
    );
  }

  get approvalRate(): number {
    if (!this.summary) {
      return 0;
    }

    const completedRequests =
      this.summary
        .approved_leave_requests +
      this.summary
        .rejected_leave_requests;

    if (completedRequests === 0) {
      return 0;
    }

    return Math.round(
      (
        this.summary
          .approved_leave_requests /
        completedRequests
      ) * 100
    );
  }

  ngOnInit(): void {
    this.loadDashboard();
  }

  loadDashboard(): void {
    this.summary = null;
    this.leaveBalance = null;
    this.errorMessage = '';
    this.isLoading = true;

    if (this.isManager) {
      this.loadManagerDashboard();
      return;
    }

    if (this.isEmployee) {
      this.loadEmployeeDashboard();
      return;
    }

    this.isLoading = false;

    this.errorMessage =
      'Kullanıcı rolü belirlenemedi.';
  }

  private loadManagerDashboard(): void {
    this.dashboardService
      .getSummary()
      .pipe(
        finalize(() => {
          this.isLoading = false;
        })
      )
      .subscribe({
        next: summary => {
          this.summary = summary;
        },

        error: (
          error: HttpErrorResponse
        ) => {
          this.errorMessage =
            this.resolveErrorMessage(
              error
            );
        }
      });
  }

  private loadEmployeeDashboard(): void {
    this.leaveService
      .getLeaveBalance()
      .pipe(
        finalize(() => {
          this.isLoading = false;
        })
      )
      .subscribe({
        next: leaveBalance => {
          this.leaveBalance =
            leaveBalance;
        },

        error: (
          error: HttpErrorResponse
        ) => {
          this.errorMessage =
            this.resolveErrorMessage(
              error
            );
        }
      });
  }

  private resolveErrorMessage(
    error: HttpErrorResponse
  ): string {
    if (error.status === 0) {
      return (
        'Sunucuya bağlanılamadı. ' +
        'Backend servisinin çalıştığını kontrol edin.'
      );
    }

    if (error.status === 401) {
      return (
        'Oturum süreniz sona ermiş olabilir. ' +
        'Yeniden giriş yapın.'
      );
    }

    if (error.status === 403) {
      return (
        'Bu verileri görüntülemek için ' +
        'yetkiniz bulunmuyor.'
      );
    }

    if (
      error.status === 404 &&
      this.isEmployee
    ) {
      return (
        'Bu kullanıcıya bağlı bir ' +
        'personel kaydı bulunamadı.'
      );
    }

    if (
      typeof error.error?.detail ===
      'string'
    ) {
      return error.error.detail;
    }

    return (
      'Dashboard verileri yüklenirken ' +
      'beklenmeyen bir hata oluştu.'
    );
  }
}
