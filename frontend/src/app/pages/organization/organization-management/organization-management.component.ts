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
import { finalize } from 'rxjs';

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

  companies: Company[] = [];
  departments: Department[] = [];
  teams: Team[] = [];

  selectedCompanyId: number | null = null;
  selectedDepartmentId: number | null = null;

  isLoadingCompanies = true;
  isLoadingDepartments = false;
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
    this.loadCompanies();
  }

  loadCompanies(): void {
    this.isLoadingCompanies = true;
    this.errorMessage = '';

    this.organizationService.getCompanies()
      .pipe(
        finalize(() => {
          this.isLoadingCompanies = false;
        })
      )
      .subscribe({
        next: companies => {
          this.companies = companies;

          if (
            this.selectedCompanyId &&
            !companies.some(
              company =>
                company.id === this.selectedCompanyId
            )
          ) {
            this.selectedCompanyId = null;
            this.selectedDepartmentId = null;
            this.departments = [];
            this.teams = [];
          }
        },
        error: error => {
          this.errorMessage =
            this.resolveError(error);
        }
      });
  }

  selectCompany(company: Company): void {
    this.selectedCompanyId = company.id;
    this.selectedDepartmentId = null;
    this.departments = [];
    this.teams = [];

    this.loadDepartments(company.id);
  }

  selectDepartment(
    department: Department
  ): void {
    this.selectedDepartmentId =
      department.id;

    this.teams = [];

    this.loadTeams(department.id);
  }

  createCompany(): void {
    if (this.companyForm.invalid) {
      this.companyForm.markAllAsTouched();
      return;
    }

    const value =
      this.companyForm.getRawValue();

    this.isSubmitting = true;
    this.errorMessage = '';
    this.successMessage = '';

    this.organizationService.createCompany({
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
          this.companies = [
            ...this.companies,
            company
          ].sort((a, b) =>
            a.name.localeCompare(
              b.name,
              'tr'
            )
          );

          this.companyForm.reset();
          this.successMessage =
            'Şirket başarıyla oluşturuldu.';
        },
        error: error => {
          this.errorMessage =
            this.resolveError(error);
        }
      });
  }

  createDepartment(): void {
    if (!this.selectedCompanyId) {
      this.errorMessage =
        'Önce bir şirket seçmelisiniz.';
      return;
    }

    if (this.departmentForm.invalid) {
      this.departmentForm.markAllAsTouched();
      return;
    }

    const value =
      this.departmentForm.getRawValue();

    this.isSubmitting = true;
    this.errorMessage = '';
    this.successMessage = '';

    this.organizationService
      .createDepartment({
        company_id:
          this.selectedCompanyId,
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
          this.departments = [
            ...this.departments,
            department
          ].sort((a, b) =>
            a.name.localeCompare(
              b.name,
              'tr'
            )
          );

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

    this.isSubmitting = true;
    this.errorMessage = '';
    this.successMessage = '';

    this.organizationService.createTeam({
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
          this.teams = [
            ...this.teams,
            team
          ].sort((a, b) =>
            a.name.localeCompare(
              b.name,
              'tr'
            )
          );

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

  deleteCompany(
    company: Company
  ): void {
    const confirmed = window.confirm(
      `${company.name} şirketini silmek istediğinizden emin misiniz?`
    );

    if (!confirmed) {
      return;
    }

    this.organizationService
      .deleteCompany(company.id)
      .subscribe({
        next: () => {
          this.companies =
            this.companies.filter(
              item => item.id !== company.id
            );

          if (
            this.selectedCompanyId ===
            company.id
          ) {
            this.selectedCompanyId = null;
            this.selectedDepartmentId = null;
            this.departments = [];
            this.teams = [];
          }

          this.successMessage =
            'Şirket silindi.';
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
      `${department.name} departmanını silmek istediğinizden emin misiniz?`
    );

    if (!confirmed) {
      return;
    }

    this.organizationService
      .deleteDepartment(department.id)
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

  deleteTeam(team: Team): void {
    const confirmed = window.confirm(
      `${team.name} takımını silmek istediğinizden emin misiniz?`
    );

    if (!confirmed) {
      return;
    }

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

  private loadDepartments(
    companyId: number
  ): void {
    this.isLoadingDepartments = true;

    this.organizationService
      .getDepartmentsByCompany(companyId)
      .pipe(
        finalize(() => {
          this.isLoadingDepartments = false;
        })
      )
      .subscribe({
        next: departments => {
          this.departments = departments;
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

    this.organizationService
      .getTeamsByDepartment(departmentId)
      .pipe(
        finalize(() => {
          this.isLoadingTeams = false;
        })
      )
      .subscribe({
        next: teams => {
          this.teams = teams;
        },
        error: error => {
          this.errorMessage =
            this.resolveError(error);
        }
      });
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

    return (
      'Organizasyon işlemi sırasında ' +
      'beklenmeyen bir hata oluştu.'
    );
  }
}
