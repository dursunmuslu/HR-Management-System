import { inject } from '@angular/core';

import {
  CanActivateFn,
  Router
} from '@angular/router';

import {
  AuthService
} from '../services/auth.service';


export const managerGuard:
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
    authService.isManager()
  ) {
    return true;
  }

  if (
    authService.isPlatformOwner()
  ) {
    return router.createUrlTree([
      '/platform'
    ]);
  }

  return router.createUrlTree([
    '/dashboard'
  ]);
};
