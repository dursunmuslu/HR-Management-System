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
  ReactiveFormsModule,
  Validators
} from '@angular/forms';

import { Router } from '@angular/router';

import {
  finalize
} from 'rxjs';

import {
  CreateEmployeeRequest
} from '../../../core/models/employee.model';

import {
  Department,
  Team
} from '../../../core/models/organization.model';

import {
  EmployeeService
} from '../../../core/services/employee.service';

import {
  OrganizationService
} from '../../../core/services/organization.service';


@Component({
  selector: 'app-employee-form',

  standalone: true,

  imports: [
    CommonModule,
    ReactiveFormsModule
  ],

  templateUrl:
    './employee-form.component.html',

  styleUrl:
    './employee-form.component.scss'
})
export class EmployeeFormComponent
  implements OnInit {

  private readonly fb = inject(FormBuilder);

  private readonly employeeService =
    inject(EmployeeService);

  private readonly organizationService =
    inject(OrganizationService);

  private readonly router = inject(Router);


  departments: Department[] = [];
  teams: Team[] = [];

  isLoadingDepartments = true;
  isLoadingTeams = false;
  isSubmitting = false;

  showPassword = false;

  errorMessage = '';


  readonly employeeForm =
    this.fb.nonNullable.group({

      username: [
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
      ],

      first_name: [
        '',
        [
          Validators.required,
          Validators.minLength(2),
          Validators.maxLength(50)
        ]
      ],

      last_name: [
        '',
        [
          Validators.required,
          Validators.minLength(2),
          Validators.maxLength(50)
        ]
      ],

      tc_no: [
        '',
        [
          Validators.required,
          Validators.pattern(
            /^[0-9]{11}$/
          )
        ]
      ],

      employee_number: [
        '',
        [
          Validators.required,
          Validators.minLength(2),
          Validators.maxLength(20)
        ]
      ],

      department_id: [
        0,
        [
          Validators.required,
          Validators.min(1)
        ]
      ],

      team_id: [
        0,
        [
          Validators.required,
          Validators.min(1)
        ]
      ],

      position: [
        '',
        [
          Validators.required,
          Validators.minLength(2),
          Validators.maxLength(100)
        ]
      ],

      phone: [
        '',
        [
          Validators.required,
          Validators.minLength(10),
          Validators.maxLength(20)
        ]
      ],

      email: [
        '',
        [
          Validators.required,
          Validators.email
        ]
      ],

      hire_date: [
        '',
        Validators.required
      ],

      remaining_annual_leave: [
        14,
        [
          Validators.required,
          Validators.min(0)
        ]
      ]
    });


  ngOnInit(): void {
    this.loadDepartments();

    this.controls.department_id
      .valueChanges
      .subscribe(departmentId => {
        this.controls.team_id.setValue(
          0,
          {
            emitEvent: false
          }
        );

        this.teams = [];

        if (departmentId > 0) {
          this.loadTeams(
            departmentId
          );
        }
      });
  }


  get controls() {
    return this.employeeForm.controls;
  }


  get selectedDepartment():
    Department | null {

    const departmentId =
      this.controls.department_id.value;

    return (
      this.departments.find(
        department =>
          department.id === departmentId
      ) ?? null
    );
  }


  togglePassword(): void {
    this.showPassword =
      !this.showPassword;
  }


  goBack(): void {
    void this.router.navigate([
      '/employees'
    ]);
  }


  submit(): void {
    this.errorMessage = '';

    if (this.employeeForm.invalid) {
      this.employeeForm.markAllAsTouched();

      this.errorMessage =
        'Lütfen zorunlu alanları doğru doldurun.';

      return;
    }

    const value =
      this.employeeForm.getRawValue();

    const selectedTeam =
      this.teams.find(
        team =>
          team.id === value.team_id
      );

    if (
      !selectedTeam ||
      !selectedTeam.is_active
    ) {
      this.errorMessage =
        'Geçerli ve aktif bir takım seçmelisiniz.';

      return;
    }

    const request:
      CreateEmployeeRequest = {

      username:
        value.username
          .trim()
          .toLowerCase(),

      temporary_password:
        value.temporary_password,

      team_id:
        Number(value.team_id),

      first_name:
        value.first_name.trim(),

      last_name:
        value.last_name.trim(),

      tc_no:
        value.tc_no.trim(),

      employee_number:
        value.employee_number.trim(),

      position:
        value.position.trim(),

      phone:
        value.phone.trim(),

      email:
        value.email
          .trim()
          .toLowerCase(),

      hire_date:
        value.hire_date,

      remaining_annual_leave:
        Number(
          value.remaining_annual_leave
        )
    };

    this.isSubmitting = true;

    this.employeeService
      .createEmployee(request)
      .pipe(
        finalize(() => {
          this.isSubmitting = false;
        })
      )
      .subscribe({
        next: () => {
          void this.router.navigate([
            '/employees'
          ]);
        },

        error: error => {
          this.errorMessage =
            this.resolveError(error);
        }
      });
  }


  private loadDepartments(): void {
    this.isLoadingDepartments = true;

    this.organizationService
      .getDepartments()
      .pipe(
        finalize(() => {
          this.isLoadingDepartments = false;
        })
      )
      .subscribe({
        next: departments => {
          this.departments =
            departments
              .filter(
                department =>
                  department.is_active
              )
              .sort(
                (first, second) =>
                  first.name.localeCompare(
                    second.name,
                    'tr'
                  )
              );
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
            teams
              .filter(
                team =>
                  team.is_active
              )
              .sort(
                (first, second) =>
                  first.name.localeCompare(
                    second.name,
                    'tr'
                  )
              );
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
        'Backend sunucusuna bağlanılamadı.'
      );
    }

    if (
      error.status === 409 &&
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

    if (
      typeof error.error?.detail ===
      'string'
    ) {
      return error.error.detail;
    }

    return (
      'Personel oluşturulamadı.'
    );
  }
}
