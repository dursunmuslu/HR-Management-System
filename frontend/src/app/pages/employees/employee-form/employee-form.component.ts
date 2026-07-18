import { CommonModule } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { Component, inject } from '@angular/core';
import {
  FormBuilder,
  ReactiveFormsModule,
  Validators
} from '@angular/forms';
import { Router } from '@angular/router';
import { finalize } from 'rxjs';

import { CreateEmployeeRequest } from '../../../core/models/employee.model';
import { EmployeeService } from '../../../core/services/employee.service';

@Component({
  selector: 'app-employee-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './employee-form.component.html',
  styleUrl: './employee-form.component.scss'
})
export class EmployeeFormComponent {
  private readonly fb = inject(FormBuilder);
  private readonly employeeService = inject(EmployeeService);
  private readonly router = inject(Router);

  isSubmitting = false;
  showPassword = false;
  errorMessage = '';

  readonly employeeForm = this.fb.nonNullable.group({
    username: ['', [Validators.required, Validators.minLength(3)]],
    password: ['', [Validators.required, Validators.minLength(6), Validators.maxLength(72)]],
    first_name: ['', [Validators.required, Validators.minLength(2)]],
    last_name: ['', [Validators.required, Validators.minLength(2)]],
    tc_no: ['', [Validators.required, Validators.pattern(/^[0-9]{11}$/)]],
    employee_number: ['', [Validators.required, Validators.minLength(2)]],
    department: ['', [Validators.required, Validators.minLength(2)]],
    position: ['', [Validators.required, Validators.minLength(2)]],
    phone: ['', [Validators.required, Validators.minLength(10)]],
    email: ['', [Validators.required, Validators.email]],
    hire_date: ['', Validators.required],
    remaining_annual_leave: [14, [Validators.required, Validators.min(0)]]
  });

  get controls() {
    return this.employeeForm.controls;
  }

  togglePassword(): void {
    this.showPassword = !this.showPassword;
  }

  goBack(): void {
    void this.router.navigate(['/employees']);
  }

  submit(): void {
    this.errorMessage = '';

    if (this.employeeForm.invalid) {
      this.employeeForm.markAllAsTouched();
      this.errorMessage = 'Lütfen zorunlu alanları doğru doldurun.';
      return;
    }

    const value = this.employeeForm.getRawValue();

    const request: CreateEmployeeRequest = {
      username: value.username.trim().toLowerCase(),
      password: value.password,
      first_name: value.first_name.trim(),
      last_name: value.last_name.trim(),
      tc_no: value.tc_no.trim(),
      employee_number: value.employee_number.trim(),
      department: value.department.trim(),
      position: value.position.trim(),
      phone: value.phone.trim(),
      email: value.email.trim().toLowerCase(),
      hire_date: value.hire_date,
      remaining_annual_leave: Number(value.remaining_annual_leave)
    };

    this.isSubmitting = true;

    this.employeeService.createEmployee(request)
      .pipe(finalize(() => this.isSubmitting = false))
      .subscribe({
        next: () => void this.router.navigate(['/employees']),
        error: (error: HttpErrorResponse) => {
          this.errorMessage = this.resolveError(error);
        }
      });
  }

  private resolveError(error: HttpErrorResponse): string {
    if (error.status === 0) {
      return 'Backend sunucusuna bağlanılamadı.';
    }

    if (error.status === 409 && typeof error.error?.detail === 'string') {
      return error.error.detail;
    }

    if (error.status === 422 && Array.isArray(error.error?.detail)) {
      return error.error.detail
        .map((item: { loc?: Array<string | number>; msg?: string }) => {
          const field = item.loc?.at(-1) ?? 'alan';
          return `${field}: ${item.msg ?? 'Geçersiz değer'}`;
        })
        .join(' | ');
    }

    if (typeof error.error?.detail === 'string') {
      return error.error.detail;
    }

    return 'Personel oluşturulamadı.';
  }
}
