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
  finalize,
  forkJoin
} from 'rxjs';

import {
  Company,
  Department,
  Team
} from '../../../core/models/organization.model';

import {
  OrganizationService
} from '../../../core/services/organization.service';


@Component({
  selector: 'app-organization-management',

  standalone: true,

  imports: [
    CommonModule,
    ReactiveFormsModule
  ],

  templateUrl:
    './organization-management.component.html',

  styleUrl:
    './organization-management.component.scss'
})
export class OrganizationManagementComponent
  implements OnInit {

  private readonly fb = inject(FormBuilder);

  private readonly organizationService =
    inject(OrganizationService);

  company: Company | null = null;

  departments: Department[] = [];
  teams: Team[] = [];

  selectedDepartmentId: number | null = null;

  isLoading = true;
  isLoadingTeams = false;
  isSubmitting = false;

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

      tax_number: [''],

      address: ['']
    });

  readonly departmentForm =
    this.fb.nonNullable.group({
      name: [
        '',
        [
          Validators.required,
          Validators.minLength(2),
          Validators.maxLength(100)
        ]
      ],

      description: ['']
    });

  readonly teamForm =
    this.fb.nonNullable.group({
      name: [
        '',
        [
          Validators.required,
          Validators.minLength(2),
          Validators.maxLength(100)
        ]
      ],

      description: ['']
    });

  ngOnInit(): void {
    this.loadOrganization();
  }

  get selectedDepartment(): Department | null {
    if (!this.selectedDepartmentId) {
      return null;
    }

    return (
      this.departments.find(
        department =>
          department.id ===
          this.selectedDepartmentId
      ) ?? null
    );
  }

  loadOrganization(): void {
    this.isLoading = true;
    this.errorMessage = '';

    forkJoin({
      company:
        this.organizationService.getMyCompany(),

      departments:
        this.organizationService.getDepartments()
    })
      .pipe(
        finalize(() => {
          this.isLoading = false;
        })
      )
      .subscribe({
        next: result => {
          this.company = result.company;

          this.departments =
            this.sortByName(result.departments);

          this.companyForm.patchValue({
            name: result.company.name,
            tax_number:
              result.company.tax_number ?? '',
            address:
              result.company.address ?? ''
          });
        },

        error: error => {
          this.errorMessage =
            this.resolveError(error);
        }
      });
  }

  selectDepartment(
    department: Department
  ): void {
    this.selectedDepartmentId =
      department.id;

    this.teams = [];

    this.loadTeams(
      department.id
    );
  }

  updateCompany(): void {
    if (this.companyForm.invalid) {
      this.companyForm.markAllAsTouched();
      return;
    }

    const value =
      this.companyForm.getRawValue();

    this.startSubmitting();

    this.organizationService
      .updateMyCompany({
        name: value.name.trim(),

        tax_number:
          value.tax_number.trim() || null,

        address:
          value.address.trim() || null
      })
      .pipe(
        finalize(() => {
          this.isSubmitting = false;
        })
      )
      .subscribe({
        next: company => {
          this.company = company;

          this.companyForm.patchValue({
            name: company.name,

            tax_number:
              company.tax_number ?? '',

            address:
              company.address ?? ''
          });

          this.successMessage =
            'Şirket bilgileri güncellendi.';
        },

        error: error => {
          this.errorMessage =
            this.resolveError(error);
        }
      });
  }

  createDepartment(): void {
    if (this.departmentForm.invalid) {
      this.departmentForm.markAllAsTouched();
      return;
    }

    const value =
      this.departmentForm.getRawValue();

    this.startSubmitting();

    this.organizationService
      .createDepartment({
        name: value.name.trim(),

        description:
          value.description.trim() || null
      })
      .pipe(
        finalize(() => {
          this.isSubmitting = false;
        })
      )
      .subscribe({
        next: department => {
          this.departments =
            this.sortByName([
              ...this.departments,
              department
            ]);

          this.departmentForm.reset();

          this.successMessage =
            'Departman başarıyla oluşturuldu.';
        },

        error: error => {
          this.errorMessage =
            this.resolveError(error);
        }
      });
  }

  toggleDepartment(
    department: Department
  ): void {
    this.clearMessages();

    const request$ =
      department.is_active
        ? this.organizationService
            .deactivateDepartment(
              department.id
            )

        : this.organizationService
            .activateDepartment(
              department.id
            );

    request$.subscribe({
      next: updatedDepartment => {
        this.replaceDepartment(
          updatedDepartment
        );

        if (
          !updatedDepartment.is_active &&
          this.selectedDepartmentId ===
          updatedDepartment.id
        ) {
          this.teams =
            this.teams.map(team => ({
              ...team,
              is_active: false
            }));
        }

        this.successMessage =
          updatedDepartment.is_active
            ? 'Departman aktifleştirildi.'
            : 'Departman pasife alındı.';
      },

      error: error => {
        this.errorMessage =
          this.resolveError(error);
      }
    });
  }

  deleteDepartment(
    department: Department
  ): void {
    const confirmed = window.confirm(
      `${department.name} departmanını kalıcı olarak silmek istediğinizden emin misiniz?`
    );

    if (!confirmed) {
      return;
    }

    this.clearMessages();

    this.organizationService
      .deleteDepartment(
        department.id
      )
      .subscribe({
        next: () => {
          this.departments =
            this.departments.filter(
              item =>
                item.id !== department.id
            );

          if (
            this.selectedDepartmentId ===
            department.id
          ) {
            this.selectedDepartmentId = null;
            this.teams = [];
          }

          this.successMessage =
            'Departman silindi.';
        },

        error: error => {
          this.errorMessage =
            this.resolveError(error);
        }
      });
  }

  createTeam(): void {
    if (!this.selectedDepartmentId) {
      this.errorMessage =
        'Önce bir departman seçmelisiniz.';

      return;
    }

    if (this.teamForm.invalid) {
      this.teamForm.markAllAsTouched();
      return;
    }

    const value =
      this.teamForm.getRawValue();

    this.startSubmitting();

    this.organizationService
      .createTeam({
        department_id:
          this.selectedDepartmentId,

        name: value.name.trim(),

        description:
          value.description.trim() || null
      })
      .pipe(
        finalize(() => {
          this.isSubmitting = false;
        })
      )
      .subscribe({
        next: team => {
          this.teams =
            this.sortByName([
              ...this.teams,
              team
            ]);

          this.teamForm.reset();

          this.successMessage =
            'Takım başarıyla oluşturuldu.';
        },

        error: error => {
          this.errorMessage =
            this.resolveError(error);
        }
      });
  }

  toggleTeam(team: Team): void {
    this.clearMessages();

    const request$ =
      team.is_active
        ? this.organizationService
            .deactivateTeam(team.id)

        : this.organizationService
            .activateTeam(team.id);

    request$.subscribe({
      next: updatedTeam => {
        this.replaceTeam(
          updatedTeam
        );

        this.successMessage =
          updatedTeam.is_active
            ? 'Takım aktifleştirildi.'
            : 'Takım pasife alındı.';
      },

      error: error => {
        this.errorMessage =
          this.resolveError(error);
      }
    });
  }

  deleteTeam(team: Team): void {
    const confirmed = window.confirm(
      `${team.name} takımını kalıcı olarak silmek istediğinizden emin misiniz?`
    );

    if (!confirmed) {
      return;
    }

    this.clearMessages();

    this.organizationService
      .deleteTeam(team.id)
      .subscribe({
        next: () => {
          this.teams =
            this.teams.filter(
              item => item.id !== team.id
            );

          this.successMessage =
            'Takım silindi.';
        },

        error: error => {
          this.errorMessage =
            this.resolveError(error);
        }
      });
  }

  private loadTeams(
    departmentId: number
  ): void {
    this.isLoadingTeams = true;
    this.errorMessage = '';

    this.organizationService
      .getTeamsByDepartment(
        departmentId
      )
      .pipe(
        finalize(() => {
          this.isLoadingTeams = false;
        })
      )
      .subscribe({
        next: teams => {
          this.teams =
            this.sortByName(teams);
        },

        error: error => {
          this.errorMessage =
            this.resolveError(error);
        }
      });
  }

  private replaceDepartment(
    updatedDepartment: Department
  ): void {
    this.departments =
      this.departments.map(
        department =>
          department.id ===
          updatedDepartment.id

            ? updatedDepartment
            : department
      );
  }

  private replaceTeam(
    updatedTeam: Team
  ): void {
    this.teams =
      this.teams.map(
        team =>
          team.id === updatedTeam.id
            ? updatedTeam
            : team
      );
  }

  private sortByName<
    T extends {
      name: string;
    }
  >(
    values: T[]
  ): T[] {
    return [...values].sort(
      (first, second) =>
        first.name.localeCompare(
          second.name,
          'tr'
        )
    );
  }

  private startSubmitting(): void {
    this.isSubmitting = true;
    this.clearMessages();
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
        'Sunucuya bağlanılamadı. ' +
        'Backend servisini kontrol edin.'
      );
    }

    if (
      typeof error.error?.detail ===
      'string'
    ) {
      return error.error.detail;
    }

    if (error.status === 401) {
      return (
        'Oturum süreniz dolmuş olabilir. ' +
        'Tekrar giriş yapın.'
      );
    }

    if (error.status === 403) {
      return (
        'Bu işlem için yetkiniz bulunmuyor.'
      );
    }

    if (error.status === 409) {
      return (
        'Bu işlem mevcut kayıtlarla ' +
        'çakıştığı için tamamlanamadı.'
      );
    }

    return (
      'Organizasyon işlemi sırasında ' +
      'beklenmeyen bir hata oluştu.'
    );
  }
}
