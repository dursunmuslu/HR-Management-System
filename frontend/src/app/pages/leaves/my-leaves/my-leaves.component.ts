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
  LeaveRequest,
  LeaveStatus
} from '../../../core/models/leave.model';

import {
  LeaveService
} from '../../../core/services/leave.service';


@Component({
  selector: 'app-my-leaves',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink
  ],
  templateUrl: './my-leaves.component.html',
  styleUrl: './my-leaves.component.scss'
})
export class MyLeavesComponent implements OnInit {

  private readonly leaveService = inject(LeaveService);

  leaves: LeaveRequest[] = [];
  filteredLeaves: LeaveRequest[] = [];

  selectedStatus = 'ALL';
  searchText = '';

  isLoading = true;
  cancellingLeaveId: number | null = null;

  errorMessage = '';
  successMessage = '';


  ngOnInit(): void {
    this.loadLeaves();
  }


  get totalCount(): number {
    return this.leaves.length;
  }


  get pendingCount(): number {
    return this.leaves.filter(
      leave => leave.status === 'PENDING'
    ).length;
  }


  get approvedCount(): number {
    return this.leaves.filter(
      leave => leave.status === 'APPROVED'
    ).length;
  }


  get rejectedCount(): number {
    return this.leaves.filter(
      leave => leave.status === 'REJECTED'
    ).length;
  }


  loadLeaves(): void {
    this.isLoading = true;
    this.errorMessage = '';

    this.leaveService.getMyLeaves()
      .pipe(
        finalize(() => {
          this.isLoading = false;
        })
      )
      .subscribe({
        next: leaves => {
          this.leaves = Array.isArray(leaves)
            ? leaves
            : [];

          this.applyFilters();
        },

        error: (error: HttpErrorResponse) => {
          this.errorMessage =
            this.resolveErrorMessage(error);
        }
      });
  }


  onStatusChange(
    event: Event
  ): void {
    const selectElement =
      event.target as HTMLSelectElement;

    this.selectedStatus =
      selectElement.value;

    this.applyFilters();
  }


  onSearchChange(
    event: Event
  ): void {
    const inputElement =
      event.target as HTMLInputElement;

    this.searchText =
      inputElement.value;

    this.applyFilters();
  }


  applyFilters(): void {
    const normalizedSearch = this.searchText
      .trim()
      .toLocaleLowerCase('tr-TR');

    this.filteredLeaves = this.leaves.filter(
      leave => {
        const matchesStatus =
          this.selectedStatus === 'ALL' ||
          leave.status === this.selectedStatus;

        const searchableText = [
          this.getLeaveTypeLabel(
            leave.leave_type
          ),
          leave.description,
          this.getStatusLabel(
            leave.status
          ),
          leave.start_date,
          leave.end_date
        ]
          .filter(Boolean)
          .join(' ')
          .toLocaleLowerCase('tr-TR');

        const matchesSearch =
          normalizedSearch.length === 0 ||
          searchableText.includes(
            normalizedSearch
          );

        return (
          matchesStatus &&
          matchesSearch
        );
      }
    );
  }


  canCancel(
    leave: LeaveRequest
  ): boolean {
    return leave.status === 'PENDING';
  }


  cancelLeave(
    leave: LeaveRequest
  ): void {
    if (!this.canCancel(leave)) {
      return;
    }

    const confirmed = window.confirm(
      'Bu izin talebini iptal etmek istediğinizden emin misiniz?'
    );

    if (!confirmed) {
      return;
    }

    this.successMessage = '';
    this.errorMessage = '';
    this.cancellingLeaveId = leave.id;

    this.leaveService.cancelLeave(leave.id)
      .pipe(
        finalize(() => {
          this.cancellingLeaveId = null;
        })
      )
      .subscribe({
        next: updatedLeave => {
          this.leaves = this.leaves.map(
            item =>
              item.id === leave.id
                ? updatedLeave
                : item
          );

          this.applyFilters();

          this.successMessage =
            'İzin talebi başarıyla iptal edildi.';
        },

        error: (error: HttpErrorResponse) => {
          this.errorMessage =
            this.resolveErrorMessage(error);
        }
      });
  }


  getLeaveDays(
    leave: LeaveRequest
  ): number {
    return leave.number_of_days ?? 0;
  }


  getLeaveTypeLabel(
    type: string
  ): string {
    const labels: Record<string, string> = {
      YILLIK_IZIN: 'Yıllık İzin',
      HASTALIK_IZNI: 'Hastalık İzni',
      MAZERET_IZNI: 'Mazeret İzni',
      UCRETSIZ_IZIN: 'Ücretsiz İzin'
    };

    return labels[type] ?? type;
  }


  getStatusLabel(
    status: LeaveStatus | string
  ): string {
    const labels: Record<string, string> = {
      PENDING: 'Beklemede',
      APPROVED: 'Onaylandı',
      REJECTED: 'Reddedildi',
      CANCELLED: 'İptal Edildi'
    };

    return labels[status] ?? status;
  }


  getStatusClass(
    status: LeaveStatus | string
  ): string {
    const classes: Record<string, string> = {
      PENDING: 'status-pending',
      APPROVED: 'status-approved',
      REJECTED: 'status-rejected',
      CANCELLED: 'status-cancelled'
    };

    return (
      classes[status] ??
      'status-default'
    );
  }


  formatDate(
    dateValue: string
  ): string {
    if (!dateValue) {
      return '-';
    }

    return new Intl.DateTimeFormat(
      'tr-TR',
      {
        day: '2-digit',
        month: 'long',
        year: 'numeric'
      }
    ).format(
      new Date(`${dateValue}T00:00:00`)
    );
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
        'Oturum süreniz dolmuş olabilir. ' +
        'Lütfen tekrar giriş yapın.'
      );
    }

    if (
      typeof error.error?.detail === 'string'
    ) {
      return error.error.detail;
    }

    if (
      Array.isArray(error.error?.detail)
    ) {
      return error.error.detail
        .map(
          (
            item: {
              msg?: string;
            }
          ) => item.msg
        )
        .filter(Boolean)
        .join(', ');
    }

    return (
      'İzin talepleri yüklenirken ' +
      'bir hata oluştu.'
    );
  }
}
