import { inject } from '@angular/core';

import {
  CanActivateFn,
  Router
} from '@angular/router';

import {
  AuthService
} from '../services/auth.service';


export const companyUserGuard:
  CanActivateFn = () => {

  const authService =
    inject(AuthService);

  const router =
    inject(Router);

  if (
    !authService.isAuthenticated()
  ) {
    return router.createUrlTree([
      '/login'
    ]);
  }

  if (
    authService.mustChangePassword()
  ) {
    return router.createUrlTree([
      '/change-password'
    ]);
  }

  if (
    authService.isCompanyUser()
  ) {
    return true;
  }

  return router.createUrlTree([
    '/platform'
  ]);
};
