import { CommonModule } from '@angular/common';

import {
  HttpErrorResponse
} from '@angular/common/http';

import {
  Component,
  OnInit,
  inject
} from '@angular/core';

import {
  FormBuilder,
  FormsModule,
  ReactiveFormsModule,
  Validators
} from '@angular/forms';

import {
  finalize,
  forkJoin
} from 'rxjs';

import {
  PlatformCompany,
  PlatformSummary
} from '../../../core/models/platform.model';

import {
  PlatformService
} from '../../../core/services/platform.service';


@Component({
  selector: 'app-platform-dashboard',

  standalone: true,

  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule
  ],

  templateUrl:
    './platform-dashboard.component.html',

  styleUrl:
    './platform-dashboard.component.scss'
})
export class PlatformDashboardComponent
  implements OnInit {

  private readonly fb =
    inject(FormBuilder);

  private readonly platformService =
    inject(PlatformService);


  summary: PlatformSummary | null = null;

  companies: PlatformCompany[] = [];

  isLoading = true;
  isSubmitting = false;

  showCreateForm = false;
  showPassword = false;

  selectedCompanyForSuspension:
    PlatformCompany | null = null;

  suspensionReason = '';

  errorMessage = '';
  successMessage = '';


  readonly companyForm =
    this.fb.nonNullable.group({

      name: [
        '',
        [
          Validators.required,
          Validators.minLength(2),
          Validators.maxLength(150)
        ]
      ],

      code: [
        '',
        [
          Validators.required,
          Validators.minLength(2),
          Validators.maxLength(30),
          Validators.pattern(
            /^[A-Za-z0-9_-]+$/
          )
        ]
      ],

      tax_number: [
        '',
        [
          Validators.maxLength(30)
        ]
      ],

      address: [
        '',
        [
          Validators.maxLength(500)
        ]
      ],

      admin_username: [
        '',
        [
          Validators.required,
          Validators.minLength(3),
          Validators.maxLength(50),
          Validators.pattern(
            /^[a-zA-Z0-9_.-]+$/
          )
        ]
      ],

      temporary_password: [
        '',
        [
          Validators.required,
          Validators.minLength(8),
          Validators.maxLength(72)
        ]
      ]
    });


  ngOnInit(): void {
    this.loadPlatformData();
  }


  get controls() {
    return this.companyForm.controls;
  }


  get activeCompanies(): number {
    return this.companies.filter(
      company => company.is_active
    ).length;
  }


  get suspendedCompanies(): number {
    return this.companies.filter(
      company => !company.is_active
    ).length;
  }


  toggleCreateForm(): void {
    this.showCreateForm =
      !this.showCreateForm;

    this.clearMessages();

    if (!this.showCreateForm) {
      this.companyForm.reset();
    }
  }


  togglePassword(): void {
    this.showPassword =
      !this.showPassword;
  }


  createCompany(): void {
    this.clearMessages();

    if (this.companyForm.invalid) {
      this.companyForm.markAllAsTouched();

      this.errorMessage =
        'Şirket ve yönetici bilgilerini doğru doldurun.';

      return;
    }

    const value =
      this.companyForm.getRawValue();

    this.isSubmitting = true;

    this.platformService
      .createCompany({
        name:
          value.name.trim(),

        code:
          value.code
            .trim()
            .toUpperCase(),

        tax_number:
          value.tax_number.trim() || null,

        address:
          value.address.trim() || null,

        admin: {
          username:
            value.admin_username
              .trim()
              .toLowerCase(),

          temporary_password:
            value.temporary_password
        }
      })
      .pipe(
        finalize(() => {
          this.isSubmitting = false;
        })
      )
      .subscribe({
        next: response => {
          this.successMessage =
            `${response.company_name} oluşturuldu. ` +
            `İlk yönetici: ${response.admin_username}`;

          this.companyForm.reset();
          this.showCreateForm = false;

          this.loadPlatformData(false);
        },

        error: error => {
          this.errorMessage =
            this.resolveError(error);
        }
      });
  }


  requestSuspend(
    company: PlatformCompany
  ): void {
    this.clearMessages();

    this.selectedCompanyForSuspension =
      company;

    this.suspensionReason = '';
  }


  cancelSuspend(): void {
    this.selectedCompanyForSuspension =
      null;

    this.suspensionReason = '';
  }


  confirmSuspend(): void {
    const company =
      this.selectedCompanyForSuspension;

    const normalizedReason =
      this.suspensionReason.trim();

    if (!company) {
      return;
    }

    if (normalizedReason.length < 5) {
      this.errorMessage =
        'Askıya alma nedeni en az 5 karakter olmalıdır.';

      return;
    }

    this.isSubmitting = true;
    this.clearMessages();

    this.platformService
      .suspendCompany(
        company.id,
        {
          reason: normalizedReason
        }
      )
      .pipe(
        finalize(() => {
          this.isSubmitting = false;
        })
      )
      .subscribe({
        next: response => {
          this.updateCompanyStatus(
            response.id,
            response.is_active,
            response.suspended_at,
            response.suspension_reason
          );

          this.selectedCompanyForSuspension =
            null;

          this.suspensionReason = '';

          this.successMessage =
            `${response.name} şirketinin erişimi askıya alındı.`;

          this.refreshSummary();
        },

        error: error => {
          this.errorMessage =
            this.resolveError(error);
        }
      });
  }


  activateCompany(
    company: PlatformCompany
  ): void {
    const confirmed =
      window.confirm(
        `${company.name} şirketinin erişimini yeniden açmak istediğinizden emin misiniz?`
      );

    if (!confirmed) {
      return;
    }

    this.isSubmitting = true;
    this.clearMessages();

    this.platformService
      .activateCompany(
        company.id
      )
      .pipe(
        finalize(() => {
          this.isSubmitting = false;
        })
      )
      .subscribe({
        next: response => {
          this.updateCompanyStatus(
            response.id,
            response.is_active,
            response.suspended_at,
            response.suspension_reason
          );

          this.successMessage =
            `${response.name} şirketinin erişimi yeniden açıldı.`;

          this.refreshSummary();
        },

        error: error => {
          this.errorMessage =
            this.resolveError(error);
        }
      });
  }


  formatDate(
    value: string | null | undefined
  ): string {
    if (!value) {
      return '-';
    }

    return new Intl.DateTimeFormat(
      'tr-TR',
      {
        dateStyle: 'medium'
      }
    ).format(
      new Date(value)
    );
  }


  private loadPlatformData(
    showLoading = true
  ): void {
    if (showLoading) {
      this.isLoading = true;
    }

    this.errorMessage = '';

    forkJoin({
      summary:
        this.platformService.getSummary(),

      companies:
        this.platformService.getCompanies()
    })
      .pipe(
        finalize(() => {
          this.isLoading = false;
        })
      )
      .subscribe({
        next: result => {
          this.summary =
            result.summary;

          this.companies =
            this.sortCompanies(
              result.companies
            );
        },

        error: error => {
          this.errorMessage =
            this.resolveError(error);
        }
      });
  }


  private refreshSummary(): void {
    this.platformService
      .getSummary()
      .subscribe({
        next: summary => {
          this.summary = summary;
        },

        error: () => {
          // Ana işlem başarılıysa yalnızca
          // özet yenileme hatasını sessiz bırakıyoruz.
        }
      });
  }


  private updateCompanyStatus(
    companyId: number,
    isActive: boolean,
    suspendedAt: string | null,
    suspensionReason: string | null
  ): void {
    this.companies =
      this.companies.map(
        company =>
          company.id === companyId
            ? {
                ...company,
                is_active: isActive,
                suspended_at: suspendedAt,
                suspension_reason:
                  suspensionReason
              }
            : company
      );
  }


  private sortCompanies(
    companies: PlatformCompany[]
  ): PlatformCompany[] {
    return [...companies].sort(
      (first, second) =>
        first.name.localeCompare(
          second.name,
          'tr'
        )
    );
  }


  private clearMessages(): void {
    this.errorMessage = '';
    this.successMessage = '';
  }


  private resolveError(
    error: HttpErrorResponse
  ): string {
    if (error.status === 0) {
      return (
        'Backend servisine bağlanılamadı.'
      );
    }

    if (
      typeof error.error?.detail ===
      'string'
    ) {
      return error.error.detail;
    }

    if (
      error.status === 422 &&
      Array.isArray(
        error.error?.detail
      )
    ) {
      return error.error.detail
        .map(
          (
            item: {
              loc?: Array<
                string | number
              >;
              msg?: string;
            }
          ) => {
            const field =
              item.loc?.at(-1) ??
              'alan';

            return (
              `${field}: ` +
              `${
                item.msg ??
                'Geçersiz değer'
              }`
            );
          }
        )
        .join(' | ');
    }

    if (error.status === 401) {
      return (
        'Oturum süreniz dolmuş olabilir.'
      );
    }

    if (error.status === 403) {
      return (
        'Bu işlem yalnızca sistem sahibi tarafından yapılabilir.'
      );
    }

    if (error.status === 409) {
      return (
        'Şirket kodu, şirket adı, vergi numarası veya yönetici kullanıcı adı zaten kullanılıyor.'
      );
    }

    return (
      'Platform işlemi sırasında ' +
      'beklenmeyen bir hata oluştu.'
    );
  }
}
