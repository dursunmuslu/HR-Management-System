import {
  HttpErrorResponse,
  HttpInterceptorFn
} from '@angular/common/http';
import { inject } from '@angular/core';
import {
  catchError,
  throwError
} from 'rxjs';

import {
  AuthService
} from '../services/auth.service';


export const authInterceptor: HttpInterceptorFn = (
  request,
  next
) => {
  const authService = inject(AuthService);
  const token = authService.getToken();

  const authorizedRequest = token
    ? request.clone({
        setHeaders: {
          Authorization: `Bearer ${token}`
        }
      })
    : request;

  return next(
    authorizedRequest
  ).pipe(
    catchError(
      (error: HttpErrorResponse) => {
        if (error.status === 401) {
          authService.logout();
        }

        return throwError(
          () => error
        );
      }
    )
  );
};
