import { CommonModule } from '@angular/common';
import { HttpErrorResponse, HttpClient } from '@angular/common/http';
import { Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { finalize } from 'rxjs';

import { Employee } from '../../../core/models/employee.model';
import { EmployeeService } from '../../../core/services/employee.service';

export type AssignableEmployeeRole =
  | 'PERSONEL'
  | 'TAKIM_LIDERI'
  | 'YONETICI';

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

  private readonly employeeService = inject(EmployeeService);
  private readonly http = inject(HttpClient);

  readonly bulkUploadUrl =
    'https://hr-management-api-6rpx.onrender.com/bulk/upload-employees';

  employees: Employee[] = [];
  filteredEmployees: Employee[] = [];

  searchText = '';
  selectedRole: 'TUMU' | AssignableEmployeeRole = 'TUMU';

  isLoading = true;
  isUploadingExcel = false;

  deletingEmployeeId: number | null = null;
  updatingRoleEmployeeId: number | null = null;

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
      employee => this.getEmployeeRole(employee) === 'YONETICI'
    ).length;
  }

  get leaderCount(): number {
    return this.employees.filter(
      employee => this.getEmployeeRole(employee) === 'TAKIM_LIDERI'
    ).length;
  }

  get personnelCount(): number {
    return this.employees.filter(
      employee => this.getEmployeeRole(employee) === 'PERSONEL'
    ).length;
  }

  get activeCount(): number {
    return this.employees.filter(
      employee => employee.is_active !== false
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
          this.employees = Array.isArray(employees)
            ? employees
            : [];

          this.applyFilters();
        },

        error: (error: HttpErrorResponse) => {
          this.employees = [];
          this.filteredEmployees = [];
          this.errorMessage = this.resolveErrorMessage(error);
        }
      });
  }

  onExcelSelected(event: Event): void {
    const input = event.target as HTMLInputElement;

    if (!input.files || input.files.length === 0) {
      return;
    }

    const file = input.files[0];

    const formData = new FormData();
    formData.append('file', file);

    this.isUploadingExcel = true;
    this.errorMessage = '';
    this.successMessage = '';

    this.http
      .post<any>(this.bulkUploadUrl, formData)
      .pipe(
        finalize(() => {
          this.isUploadingExcel = false;
          input.value = '';
        })
      )
      .subscribe({
        next: res => {
          this.successMessage =
            res.message || 'Excel başarıyla yüklendi!';

          this.loadEmployees();
        },

        error: (err: HttpErrorResponse) => {
          this.errorMessage =
            'Excel Hatası: ' +
            (err.error?.detail || err.message);
        }
      });
  }

  applyFilters(): void {
    const search = this.searchText
      .trim()
      .toLocaleLowerCase('tr-TR');

    this.filteredEmployees = this.employees.filter(employee => {

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
        employee.team?.name ??
          (employee as any).team_name ??
          '',
        employee.position ?? '',
        employee.employee_number ?? '',
        employee.tc_no ?? '',
        this.getRoleLabel(employeeRole)
      ]
        .filter(
          value =>
            typeof value === 'string' &&
            value.trim().length > 0
        )
        .join(' ')
        .toLocaleLowerCase('tr-TR');

      const searchMatches =
        search.length === 0 ||
        searchableText.includes(search);

      return roleMatches && searchMatches;
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

    const selectedValue =
      selectElement.value;

    if (!this.isAssignableRole(selectedValue)) {
      selectElement.value = previousRole;

      this.errorMessage =
        'Geçersiz kullanıcı rolü seçildi.';

      return;
    }

    const newRole: AssignableEmployeeRole =
      selectedValue;

    if (newRole === previousRole) {
      return;
    }

    const employeeName =
      this.getFullName(employee);

    const newRoleLabel =
      this.getRoleLabel(newRole);

    const confirmed = window.confirm(
      `${employeeName} kullanıcısının rolü "${newRoleLabel}" olarak değiştirilsin mi?`
    );

    if (!confirmed) {
      selectElement.value = previousRole;
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
          this.updatingRoleEmployeeId = null;
        })
      )
      .subscribe({
        next: updatedUser => {

          employee.role =
            updatedUser.role;

          employee.username =
            updatedUser.username;

          employee.is_active =
            updatedUser.is_active;

          if (employee.user) {
            employee.user.role =
              updatedUser.role;
          }

          this.applyFilters();

          this.successMessage =
            `${employeeName} kullanıcısının rolü ${this.getRoleLabel(updatedUser.role)} yapıldı.`;
        },

        error: (error: HttpErrorResponse) => {

          selectElement.value =
            previousRole;

          this.errorMessage =
            this.resolveErrorMessage(error);
        }
      });
  }

  deleteEmployee(employee: Employee): void {

    const employeeName =
      this.getFullName(employee);

    const confirmed = window.confirm(
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
          this.deletingEmployeeId = null;
        })
      )
      .subscribe({
        next: () => {

          this.employees =
            this.employees.filter(
              item => item.id !== employee.id
            );

          this.applyFilters();

          this.successMessage =
            'Personel silindi.';
        },

        error: (error: HttpErrorResponse) => {
          this.errorMessage =
            this.resolveErrorMessage(error);
        }
      });
  }

  getEmployeeRole(
    employee: Employee
  ): AssignableEmployeeRole {

    const role =
      employee.role ??
      employee.user?.role;

    if (role === 'YONETICI') {
      return 'YONETICI';
    }

    if (role === 'TAKIM_LIDERI') {
      return 'TAKIM_LIDERI';
    }

    return 'PERSONEL';
  }

  getFullName(employee: Employee): string {

    if (
      typeof employee.full_name === 'string' &&
      employee.full_name.trim()
    ) {
      return employee.full_name.trim();
    }

    const fullName = [
      employee.first_name ?? '',
      employee.last_name ?? ''
    ]
      .filter(
        value => value.trim().length > 0
      )
      .join(' ')
      .trim();

    return (
      fullName ||
      employee.username ||
      `Personel #${employee.id}`
    );
  }

  getDisplayUsername(
    employee: Employee
  ): string {

    if (employee.username) {
      return employee.username;
    }

    if (
      employee.email &&
      typeof employee.email === 'string'
    ) {
      const parts =
        employee.email.split('@');

      return parts.length > 0
        ? parts[0]
        : 'kullanici';
    }

    return 'kullanici';
  }

  getTeamName(employee: any): string {
    return (
      employee.team?.name ||
      employee.team_name ||
      'Genel Ekip'
    );
  }

  getLeaveBalance(
    employee: Employee
  ): number {
    return employee.remaining_annual_leave ?? 0;
  }

  getInitials(
    employee: Employee
  ): string {

    return this.getFullName(employee)
      .split(' ')
      .filter(Boolean)
      .slice(0, 2)
      .map(part => part.charAt(0))
      .join('')
      .toLocaleUpperCase('tr-TR');
  }

  getRoleLabel(
    role: string | null | undefined
  ): string {

    if (role === 'YONETICI') {
      return 'Yönetici';
    }

    if (role === 'TAKIM_LIDERI') {
      return 'Takım Lideri';
    }

    if (role === 'PERSONEL') {
      return 'Personel';
    }

    return 'Belirtilmemiş';
  }

  private isAssignableRole(
    value: string
  ): value is AssignableEmployeeRole {

    return (
      value === 'PERSONEL' ||
      value === 'TAKIM_LIDERI' ||
      value === 'YONETICI'
    );
  }

  private resolveErrorMessage(
    error: HttpErrorResponse
  ): string {

    if (error.status === 0) {
      return 'Sunucuya bağlanılamadı.';
    }

    if (
      typeof error.error?.detail === 'string'
    ) {
      return error.error.detail;
    }

    return 'Personel işlemi sırasında hata oluştu.';
  }
}
