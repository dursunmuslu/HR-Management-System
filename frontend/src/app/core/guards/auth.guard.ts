import { inject } from '@angular/core';

import {
  CanActivateFn,
  Router
} from '@angular/router';

import {
  AuthService
} from '../services/auth.service';


export const authGuard:
  CanActivateFn = (
    route
  ) => {

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

  const requestedPath =
    route.routeConfig?.path;

  if (
    authService.mustChangePassword() &&
    requestedPath !==
      'change-password'
  ) {
    return router.createUrlTree([
      '/change-password'
    ]);
  }

  return true;
};
