import { CommonModule } from '@angular/common';

import {
  HttpErrorResponse
} from '@angular/common/http';

import {
  Component,
  inject
} from '@angular/core';

import {
  AbstractControl,
  FormBuilder,
  ReactiveFormsModule,
  ValidationErrors,
  Validators
} from '@angular/forms';

import { Router } from '@angular/router';

import { finalize } from 'rxjs';

import {
  AuthService
} from '../../core/services/auth.service';


@Component({
  selector: 'app-change-password',

  standalone: true,

  imports: [
    CommonModule,
    ReactiveFormsModule
  ],

  templateUrl:
    './change-password.component.html',

  styleUrl:
    './change-password.component.scss'
})
export class ChangePasswordComponent {

  private readonly fb =
    inject(FormBuilder);

  private readonly authService =
    inject(AuthService);

  private readonly router =
    inject(Router);


  isSubmitting = false;

  showCurrentPassword = false;
  showNewPassword = false;

  errorMessage = '';


  readonly form =
    this.fb.nonNullable.group(
      {
        current_password: [
          '',
          [
            Validators.required,
            Validators.maxLength(72)
          ]
        ],

        new_password: [
          '',
          [
            Validators.required,
            Validators.minLength(8),
            Validators.maxLength(72)
          ]
        ],

        new_password_confirmation: [
          '',
          [
            Validators.required,
            Validators.minLength(8),
            Validators.maxLength(72)
          ]
        ]
      },
      {
        validators:
          this.passwordMatchValidator
      }
    );


  get controls() {
    return this.form.controls;
  }


  toggleCurrentPassword(): void {
    this.showCurrentPassword =
      !this.showCurrentPassword;
  }


  toggleNewPassword(): void {
    this.showNewPassword =
      !this.showNewPassword;
  }


  submit(): void {
    this.errorMessage = '';

    if (this.form.invalid) {
      this.form.markAllAsTouched();

      this.errorMessage =
        'Şifre alanlarını doğru doldurun.';

      return;
    }

    this.isSubmitting = true;

    this.authService
      .changePassword(
        this.form.getRawValue()
      )
      .pipe(
        finalize(() => {
          this.isSubmitting = false;
        })
      )
      .subscribe({
        next: user => {
          const destination =
            user.role ===
            'PLATFORM_OWNER'
              ? '/platform'
              : '/dashboard';

          void this.router.navigate([
            destination
          ]);
        },

        error: error => {
          this.errorMessage =
            this.resolveError(error);
        }
      });
  }


  logout(): void {
    this.authService.logout();
  }


  private passwordMatchValidator(
    control: AbstractControl
  ): ValidationErrors | null {
    const password =
      control.get(
        'new_password'
      )?.value;

    const confirmation =
      control.get(
        'new_password_confirmation'
      )?.value;

    if (
      password &&
      confirmation &&
      password !== confirmation
    ) {
      return {
        passwordMismatch: true
      };
    }

    return null;
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
              msg?: string;
            }
          ) =>
            item.msg ??
            'Geçersiz değer'
        )
        .join(' | ');
    }

    return (
      'Şifre değiştirilemedi.'
    );
  }
}
