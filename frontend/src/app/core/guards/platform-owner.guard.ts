import { inject } from '@angular/core';

import {
  CanActivateFn,
  Router
} from '@angular/router';

import {
  AuthService
} from '../services/auth.service';


export const platformOwnerGuard:
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
    authService.isPlatformOwner()
  ) {
    return true;
  }

  return router.createUrlTree([
    '/dashboard'
  ]);
};
