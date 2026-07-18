import { CommonModule } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import {
  Component,
  OnInit,
  inject
} from '@angular/core';
import {
  FormBuilder,
  ReactiveFormsModule,
  Validators
} from '@angular/forms';
import {
  Router,
  RouterLink
} from '@angular/router';
import { finalize } from 'rxjs';

import {
  CreateLeaveRequest,
  LeaveBalance,
  LeaveType
} from '../../../core/models/leave.model';

import {
  LeaveService
} from '../../../core/services/leave.service';

@Component({
  selector: 'app-create-leave',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    RouterLink
  ],
  templateUrl: './create-leave.component.html',
  styleUrl: './create-leave.component.scss'
})
export class CreateLeaveComponent implements OnInit {

  private readonly formBuilder = inject(FormBuilder);
  private readonly leaveService = inject(LeaveService);
  private readonly router = inject(Router);

  isSubmitting = false;
  isBalanceLoading = true;
  errorMessage = '';

  leaveBalance: LeaveBalance | null = null;

  readonly today = this.formatDateForInput(
    new Date()
  );

  readonly leaveForm =
    this.formBuilder.nonNullable.group({
      leave_type: [
        'YILLIK_IZIN' as LeaveType,
        [
          Validators.required
        ]
      ],

      start_date: [
        '',
        [
          Validators.required
        ]
      ],

      end_date: [
        '',
        [
          Validators.required
        ]
      ],

      description: [
        '',
        [
          Validators.required,
          Validators.minLength(10),
          Validators.maxLength(500)
        ]
      ]
    });

  ngOnInit(): void {
    this.loadLeaveBalance();
  }

  get startDateControl() {
    return this.leaveForm.controls.start_date;
  }

  get endDateControl() {
    return this.leaveForm.controls.end_date;
  }

  get descriptionControl() {
    return this.leaveForm.controls.description;
  }

  get leaveTypeControl() {
    return this.leaveForm.controls.leave_type;
  }

  get calculatedDays(): number {
    const startDate =
      this.startDateControl.value;

    const endDate =
      this.endDateControl.value;

    if (!startDate || !endDate) {
      return 0;
    }

    const start = new Date(
      `${startDate}T00:00:00`
    );

    const end = new Date(
      `${endDate}T00:00:00`
    );

    if (end < start) {
      return 0;
    }

    const difference =
      end.getTime() - start.getTime();

    return Math.floor(
      difference /
      (1000 * 60 * 60 * 24)
    ) + 1;
  }

  get remainingAnnualLeave(): number {
    return (
      this.leaveBalance
        ?.remaining_annual_leave ??
      0
    );
  }

  onStartDateChange(): void {
    const startDate =
      this.startDateControl.value;

    const endDate =
      this.endDateControl.value;

    if (
      startDate &&
      endDate &&
      endDate < startDate
    ) {
      this.endDateControl.setValue('');
    }
  }

  submit(): void {
    this.errorMessage = '';

    if (this.leaveForm.invalid) {
      this.leaveForm.markAllAsTouched();
      return;
    }

    if (this.calculatedDays <= 0) {
      this.errorMessage =
        'Bitiş tarihi başlangıç tarihinden önce olamaz.';

      return;
    }

    if (
      this.leaveTypeControl.value ===
        'YILLIK_IZIN' &&
      this.calculatedDays >
        this.remainingAnnualLeave
    ) {
      this.errorMessage =
        'Talep edilen izin süresi kalan yıllık izin bakiyesinden fazladır.';

      return;
    }

    const formValue =
      this.leaveForm.getRawValue();

    const request: CreateLeaveRequest = {
      leave_type:
        formValue.leave_type,

      start_date:
        formValue.start_date,

      end_date:
        formValue.end_date,

      description:
        formValue.description.trim()
    };

    this.isSubmitting = true;

    this.leaveService
      .createLeave(request)
      .pipe(
        finalize(() => {
          this.isSubmitting = false;
        })
      )
      .subscribe({
        next: () => {
          void this.router.navigate(
            ['/leaves/my'],
            {
              state: {
                message:
                  'İzin talebi başarıyla oluşturuldu.'
              }
            }
          );
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

  private loadLeaveBalance(): void {
    this.isBalanceLoading = true;

    this.leaveService
      .getLeaveBalance()
      .pipe(
        finalize(() => {
          this.isBalanceLoading = false;
        })
      )
      .subscribe({
        next: balance => {
          this.leaveBalance = balance;
        },

        error: () => {
          this.leaveBalance = null;
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
        'Lütfen tekrar giriş yapın.'
      );
    }

    if (error.status === 403) {
      return (
        'Bu işlemi gerçekleştirmek için ' +
        'personel yetkisi gerekiyor.'
      );
    }

    if (
      typeof error.error?.detail ===
      'string'
    ) {
      return error.error.detail;
    }

    if (
      Array.isArray(
        error.error?.detail
      )
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
      'İzin talebi oluşturulurken ' +
      'bir hata oluştu.'
    );
  }

  private formatDateForInput(
    date: Date
  ): string {
    const year =
      date.getFullYear();

    const month = String(
      date.getMonth() + 1
    ).padStart(2, '0');

    const day = String(
      date.getDate()
    ).padStart(2, '0');

    return `${year}-${month}-${day}`;
  }
}
