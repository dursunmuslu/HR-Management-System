import { CommonModule } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import {
  Component,
  OnInit,
  inject
} from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { finalize } from 'rxjs';

import {
  Employee,
  EmployeeRole
} from '../../../core/models/employee.model';

import {
  EmployeeService
} from '../../../core/services/employee.service';

@Component({
  selector: 'app-employee-list',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterLink
  ],
  templateUrl: './employee-list.component.html',
  styleUrl: './employee-list.component.scss'
})
export class EmployeeListComponent implements OnInit {
  private readonly employeeService =
    inject(EmployeeService);

  employees: Employee[] = [];
  filteredEmployees: Employee[] = [];

  searchText = '';
  selectedRole:
    | 'TUMU'
    | EmployeeRole = 'TUMU';

  isLoading = true;

  deletingEmployeeId:
    number | null = null;

  updatingRoleEmployeeId:
    number | null = null;

  errorMessage = '';
  successMessage = '';

  ngOnInit(): void {
    this.loadEmployees();
  }

  get totalCount(): number {
    return this.employees.length;
  }

  get managerCount(): number {
    return this.employees.filter(
      employee =>
        this.getEmployeeRole(employee) ===
        'YONETICI'
    ).length;
  }

  get personnelCount(): number {
    return this.employees.filter(
      employee =>
        this.getEmployeeRole(employee) ===
        'PERSONEL'
    ).length;
  }

  get activeCount(): number {
    return this.employees.filter(
      employee =>
        employee.is_active !== false
    ).length;
  }

  loadEmployees(): void {
    this.isLoading = true;
    this.errorMessage = '';
    this.successMessage = '';

    this.employeeService
      .getEmployees()
      .pipe(
        finalize(() => {
          this.isLoading = false;
        })
      )
      .subscribe({
        next: employees => {
          this.employees =
            Array.isArray(employees)
              ? employees
              : [];

          this.applyFilters();
        },

        error: (
          error: HttpErrorResponse
        ) => {
          this.employees = [];
          this.filteredEmployees = [];

          this.errorMessage =
            this.resolveErrorMessage(error);
        }
      });
  }

  applyFilters(): void {
    const search = this.searchText
      .trim()
      .toLocaleLowerCase('tr-TR');

    this.filteredEmployees =
      this.employees.filter(employee => {
        const employeeRole =
          this.getEmployeeRole(employee);

        const roleMatches =
          this.selectedRole === 'TUMU' ||
          employeeRole === this.selectedRole;

        const searchableText = [
          this.getFullName(employee),
          employee.username ?? '',
          employee.email ?? '',
          employee.department ?? '',
          employee.position ?? '',
          employee.employee_number ?? '',
          employee.tc_no ?? '',
          this.getRoleLabel(employeeRole)
        ]
          .filter(
            value =>
              value.trim().length > 0
          )
          .join(' ')
          .toLocaleLowerCase('tr-TR');

        const searchMatches =
          search.length === 0 ||
          searchableText.includes(search);

        return (
          roleMatches &&
          searchMatches
        );
      });
  }

  clearFilters(): void {
    this.searchText = '';
    this.selectedRole = 'TUMU';
    this.applyFilters();
  }

  changeRole(
    employee: Employee,
    event: Event
  ): void {
    const selectElement =
      event.target as HTMLSelectElement;

    const previousRole =
      this.getEmployeeRole(employee);

    const newRole =
      selectElement.value as EmployeeRole;

    if (newRole === previousRole) {
      return;
    }

    const employeeName =
      this.getFullName(employee);

    const newRoleLabel =
      this.getRoleLabel(newRole);

    const confirmed =
      window.confirm(
        `${employeeName} isimli kullanıcının rolü "${newRoleLabel}" olarak değiştirilsin mi?`
      );

    if (!confirmed) {
      selectElement.value =
        previousRole;

      return;
    }

    this.errorMessage = '';
    this.successMessage = '';

    this.updatingRoleEmployeeId =
      employee.id;

    this.employeeService
      .updateUserRole(
        employee.user_id,
        newRole
      )
      .pipe(
        finalize(() => {
          this.updatingRoleEmployeeId =
            null;
        })
      )
      .subscribe({
        next: updatedUser => {
          employee.role =
            updatedUser.role;

          employee.username =
            updatedUser.username;

          if (employee.user) {
            employee.user = {
              ...employee.user,
              id: updatedUser.id,
              username:
                updatedUser.username,
              role:
                updatedUser.role
            };
          }

          this.applyFilters();

          this.successMessage =
            `${employeeName} kullanıcısının rolü ${this.getRoleLabel(updatedUser.role)} olarak güncellendi.`;
        },

        error: (
          error: HttpErrorResponse
        ) => {
          selectElement.value =
            previousRole;

          this.errorMessage =
            this.resolveErrorMessage(error);
        }
      });
  }

  deleteEmployee(
    employee: Employee
  ): void {
    const employeeName =
      this.getFullName(employee);

    const confirmed =
      window.confirm(
        `${employeeName} isimli personeli silmek istediğinizden emin misiniz?`
      );

    if (!confirmed) {
      return;
    }

    this.errorMessage = '';
    this.successMessage = '';

    this.deletingEmployeeId =
      employee.id;

    this.employeeService
      .deleteEmployee(employee.id)
      .pipe(
        finalize(() => {
          this.deletingEmployeeId =
            null;
        })
      )
      .subscribe({
        next: () => {
          this.employees =
            this.employees.filter(
              item =>
                item.id !== employee.id
            );

          this.applyFilters();

          this.successMessage =
            'Personel kaydı başarıyla silindi.';
        },

        error: (
          error: HttpErrorResponse
        ) => {
          this.errorMessage =
            this.resolveErrorMessage(error);
        }
      });
  }

  getEmployeeRole(
    employee: Employee
  ): EmployeeRole {
    const role =
      employee.role ??
      employee.user?.role;

    return role === 'YONETICI'
      ? 'YONETICI'
      : 'PERSONEL';
  }

  getFullName(
    employee: Employee
  ): string {
    if (
      typeof employee.full_name ===
        'string' &&
      employee.full_name.trim()
    ) {
      return employee.full_name.trim();
    }

    const fullName = [
      employee.first_name ?? '',
      employee.last_name ?? ''
    ]
      .filter(
        value =>
          value.trim().length > 0
      )
      .join(' ')
      .trim();

    return (
      fullName ||
      employee.username ||
      employee.employee_number ||
      `Personel #${employee.id}`
    );
  }

  getInitials(
    employee: Employee
  ): string {
    return this.getFullName(employee)
      .split(' ')
      .filter(Boolean)
      .slice(0, 2)
      .map(
        part =>
          part.charAt(0)
      )
      .join('')
      .toLocaleUpperCase('tr-TR');
  }

  getRoleLabel(
    role:
      | string
      | null
      | undefined
  ): string {
    if (role === 'YONETICI') {
      return 'Yönetici';
    }

    if (role === 'PERSONEL') {
      return 'Personel';
    }

    return 'Belirtilmemiş';
  }

  getLeaveBalance(
    employee: Employee
  ): number {
    return (
      employee.remaining_annual_leave ??
      0
    );
  }

  private resolveErrorMessage(
    error: HttpErrorResponse
  ): string {
    if (error.status === 0) {
      return 'Sunucuya bağlanılamadı. Backend servisinin çalıştığını kontrol edin.';
    }

    if (error.status === 400) {
      return typeof error.error?.detail ===
        'string'
        ? error.error.detail
        : 'Bu işlem gerçekleştirilemedi.';
    }

    if (error.status === 401) {
      return 'Oturum süreniz dolmuş olabilir. Tekrar giriş yapın.';
    }

    if (error.status === 403) {
      return 'Bu işlem için yönetici yetkisi gereklidir.';
    }

    if (error.status === 404) {
      return typeof error.error?.detail ===
        'string'
        ? error.error.detail
        : 'Kullanıcı veya personel kaydı bulunamadı.';
    }

    if (error.status === 422) {
      return 'Gönderilen rol veya personel bilgileri geçersiz.';
    }

    if (
      typeof error.error?.detail ===
      'string'
    ) {
      return error.error.detail;
    }

    return 'Personel işlemi sırasında beklenmeyen bir hata oluştu.';
  }
}
