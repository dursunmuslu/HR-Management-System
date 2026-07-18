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
  FormsModule
} from '@angular/forms';

import {
  finalize
} from 'rxjs';

import {
  LeaveActionRequest,
  LeaveRequest,
  LeaveStatus
} from '../../../core/models/leave.model';

import {
  LeaveService
} from '../../../core/services/leave.service';


type ActionType = 'approve' | 'reject';


@Component({
  selector: 'app-leave-requests',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule
  ],
  templateUrl: './leave-requests.component.html',
  styleUrl: './leave-requests.component.scss'
})
export class LeaveRequestsComponent implements OnInit {

  private readonly leaveService = inject(LeaveService);

  leaves: LeaveRequest[] = [];
  filteredLeaves: LeaveRequest[] = [];

  selectedStatus = 'ALL';
  searchText = '';

  isLoading = true;
  errorMessage = '';
  successMessage = '';

  selectedLeave: LeaveRequest | null = null;
  selectedAction: ActionType | null = null;

  managerNote = '';
  isProcessing = false;


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

    this.leaveService.getAllLeaves()
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


  applyFilters(): void {
    const search = this.searchText
      .trim()
      .toLocaleLowerCase('tr-TR');

    this.filteredLeaves = this.leaves.filter(
      leave => {
        const matchesStatus =
          this.selectedStatus === 'ALL' ||
          leave.status === this.selectedStatus;

        const searchableText = [
          this.getEmployeeName(leave),
          leave.employee?.employee_number,
          leave.employee?.department,
          leave.employee?.position,
          leave.description,
          leave.start_date,
          leave.end_date,
          this.getLeaveTypeLabel(
            leave.leave_type
          ),
          this.getStatusLabel(
            leave.status
          )
        ]
          .filter(Boolean)
          .join(' ')
          .toLocaleLowerCase('tr-TR');

        const matchesSearch =
          search.length === 0 ||
          searchableText.includes(search);

        return (
          matchesStatus &&
          matchesSearch
        );
      }
    );
  }


  openActionModal(
    leave: LeaveRequest,
    action: ActionType
  ): void {
    if (!this.isPending(leave.status)) {
      return;
    }

    this.selectedLeave = leave;
    this.selectedAction = action;

    this.managerNote = '';
    this.errorMessage = '';
    this.successMessage = '';
  }


  closeActionModal(): void {
    if (this.isProcessing) {
      return;
    }

    this.selectedLeave = null;
    this.selectedAction = null;
    this.managerNote = '';
  }


  confirmAction(): void {
    if (
      this.selectedLeave === null ||
      this.selectedAction === null
    ) {
      return;
    }

    const trimmedManagerNote =
      this.managerNote.trim();

    /*
     * Backend LeaveReject şeması,
     * reddetme notunda minimum 3 karakter bekliyor.
     */
    if (
      this.selectedAction === 'reject' &&
      trimmedManagerNote.length < 3
    ) {
      this.errorMessage =
        'Reddetme işlemi için en az 3 karakterlik bir yönetici notu girin.';

      return;
    }

    const leaveId = this.selectedLeave.id;
    const action = this.selectedAction;

    const request: LeaveActionRequest = {
      manager_note:
        trimmedManagerNote.length > 0
          ? trimmedManagerNote
          : null
    };

    this.isProcessing = true;
    this.errorMessage = '';
    this.successMessage = '';

    const operation$ =
      action === 'approve'
        ? this.leaveService.approveLeave(
            leaveId,
            request
          )
        : this.leaveService.rejectLeave(
            leaveId,
            request
          );

    operation$
      .pipe(
        finalize(() => {
          this.isProcessing = false;
        })
      )
      .subscribe({
        next: updatedLeave => {
          this.leaves = this.leaves.map(
            leave => {
              if (leave.id !== leaveId) {
                return leave;
              }

              return {
                ...leave,
                ...updatedLeave
              };
            }
          );

          this.applyFilters();

          this.successMessage =
            action === 'approve'
              ? 'İzin talebi başarıyla onaylandı.'
              : 'İzin talebi başarıyla reddedildi.';

          this.selectedLeave = null;
          this.selectedAction = null;
          this.managerNote = '';
        },

        error: (error: HttpErrorResponse) => {
          this.errorMessage =
            this.resolveErrorMessage(error);
        }
      });
  }


  getEmployeeName(
    leave: LeaveRequest
  ): string {
    if (leave.employee) {
      return [
        leave.employee.first_name,
        leave.employee.last_name
      ]
        .filter(Boolean)
        .join(' ');
    }

    return `Personel #${leave.employee_id}`;
  }


  getEmployeeInitial(
    leave: LeaveRequest
  ): string {
    return this.getEmployeeName(leave)
      .charAt(0)
      .toLocaleUpperCase('tr-TR');
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


  isPending(
    status: LeaveStatus | string
  ): boolean {
    return status === 'PENDING';
  }


  isApproved(
    status: LeaveStatus | string
  ): boolean {
    return status === 'APPROVED';
  }


  isRejected(
    status: LeaveStatus | string
  ): boolean {
    return status === 'REJECTED';
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
        month: 'short',
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

    if (error.status === 403) {
      return (
        'Bu işlem için yönetici yetkisi gerekiyor.'
      );
    }

    if (error.status === 405) {
      return (
        'İstek metodu backend endpointiyle uyuşmuyor.'
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
      'İzin talepleri işlenirken ' +
      'beklenmeyen bir hata oluştu.'
    );
  }
}
