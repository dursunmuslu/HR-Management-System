import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  FormBuilder,
  ReactiveFormsModule,
  Validators
} from '@angular/forms';
import { Router } from '@angular/router';
import {
  HttpErrorResponse
} from '@angular/common/http';
import {
  finalize,
  switchMap
} from 'rxjs';

import {
  AuthService
} from '../../core/services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule
  ],
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss'
})
export class LoginComponent {

  private readonly formBuilder = inject(FormBuilder);
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);

  isLoading = false;
  showPassword = false;
  errorMessage = '';

  readonly loginForm = this.formBuilder.nonNullable.group({
    username: [
      '',
      [
        Validators.required
      ]
    ],
    password: [
      '',
      [
        Validators.required,
        Validators.minLength(6)
      ]
    ]
  });

  get usernameControl() {
    return this.loginForm.controls.username;
  }

  get passwordControl() {
    return this.loginForm.controls.password;
  }

  togglePasswordVisibility(): void {
    this.showPassword = !this.showPassword;
  }

  submit(): void {
    this.errorMessage = '';

    if (this.loginForm.invalid) {
      this.loginForm.markAllAsTouched();
      return;
    }

    this.isLoading = true;

    this.authService.login(
      this.loginForm.getRawValue()
    ).pipe(
      switchMap(() => {
        return this.authService.getCurrentUser();
      }),
      finalize(() => {
        this.isLoading = false;
      })
    ).subscribe({
      next: () => {
        void this.router.navigate(['/dashboard']);
      },
      error: (error: HttpErrorResponse) => {
        this.errorMessage = this.resolveErrorMessage(error);
      }
    });
  }

  private resolveErrorMessage(
    error: HttpErrorResponse
  ): string {
    if (error.status === 0) {
      return 'Sunucuya bağlanılamadı. Backend servisinin çalıştığını kontrol edin.';
    }

    if (error.status === 401) {
      return 'Kullanıcı adı veya şifre hatalı.';
    }

    if (typeof error.error?.detail === 'string') {
      return error.error.detail;
    }

    return 'Giriş işlemi sırasında beklenmeyen bir hata oluştu.';
  }
}
