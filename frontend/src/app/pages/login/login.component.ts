import { CommonModule } from '@angular/common';

import {
  HttpErrorResponse
} from '@angular/common/http';

import {
  Component,
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
  AuthService
} from '../../core/services/auth.service';


@Component({
  selector: 'app-login',

  standalone: true,

  imports: [
    CommonModule,
    ReactiveFormsModule
  ],

  templateUrl:
    './login.component.html',

  styleUrl:
    './login.component.scss'
})
export class LoginComponent {

  private readonly formBuilder =
    inject(FormBuilder);

  private readonly authService =
    inject(AuthService);

  private readonly router =
    inject(Router);


  isLoading = false;
  showPassword = false;
  errorMessage = '';


  readonly loginForm =
    this.formBuilder.nonNullable.group({

      username: [
        '',
        [
          Validators.required,
          Validators.minLength(3),
          Validators.maxLength(50)
        ]
      ],

      password: [
        '',
        [
          Validators.required,
          Validators.minLength(1),
          Validators.maxLength(72)
        ]
      ]
    });


  get usernameControl() {
    return this.loginForm
      .controls.username;
  }


  get passwordControl() {
    return this.loginForm
      .controls.password;
  }


  togglePasswordVisibility(): void {
    this.showPassword =
      !this.showPassword;
  }


  submit(): void {
    this.errorMessage = '';

    if (this.loginForm.invalid) {
      this.loginForm.markAllAsTouched();
      return;
    }

    const rawValue =
      this.loginForm.getRawValue();

    this.isLoading = true;

    this.authService
      .login({
        username:
          rawValue.username
            .trim()
            .toLowerCase(),

        password:
          rawValue.password
      })
      .pipe(
        finalize(() => {
          this.isLoading = false;
        })
      )
      .subscribe({
        next: response => {
          const destination =
            response.must_change_password
              ? '/change-password'

              : response.user.role ===
                'PLATFORM_OWNER'
                ? '/platform'

                : '/dashboard';

          void this.router.navigate([
            destination
          ]);
        },

        error: error => {
          this.errorMessage =
            this.resolveErrorMessage(
              error
            );
        }
      });
  }


  private resolveErrorMessage(
    error: HttpErrorResponse
  ): string {
    if (error.status === 0) {
      return (
        'Sunucuya bağlanılamadı. ' +
        'Backend servisinin çalıştığını ' +
        'kontrol edin.'
      );
    }

    if (error.status === 401) {
      return (
        'Kullanıcı adı veya şifre hatalı.'
      );
    }

    if (error.status === 403) {
      if (
        typeof error.error?.detail ===
        'string'
      ) {
        return error.error.detail;
      }

      return (
        'Hesabınız veya şirket erişiminiz ' +
        'devre dışı bırakılmış.'
      );
    }

    if (
      typeof error.error?.detail ===
      'string'
    ) {
      return error.error.detail;
    }

    return (
      'Giriş işlemi sırasında beklenmeyen ' +
      'bir hata oluştu.'
    );
  }
}
