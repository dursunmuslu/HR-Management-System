import { inject } from '@angular/core';
import { CanActivateFn, Router, ActivatedRouteSnapshot } from '@angular/router';
import { map, take } from 'rxjs/operators';
import { AuthService } from '../services/auth.service';

export const authGuard: CanActivateFn = (route: ActivatedRouteSnapshot) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  // 1. Oturum Kontrolü
  if (!authService.isAuthenticated()) {
    return router.createUrlTree(['/login']);
  }

  // 2. Şifre Değiştirme Zorunluluğu
  const requestedPath = route.routeConfig?.path;
  if (authService.mustChangePassword() && requestedPath !== 'change-password') {
    return router.createUrlTree(['/change-password']);
  }

  // 3. Rol Yetki Kontrolü
  const expectedRoles = route.data?.['roles'] as Array<string> | undefined;

  if (expectedRoles && expectedRoles.length > 0) {
    return authService.getCurrentUser().pipe(
      take(1),
      map((user) => {
        const userRole = user?.role;
        if (!userRole || !expectedRoles.includes(userRole)) {
          return router.createUrlTree(['/dashboard']);
        }
        return true;
      })
    );
  }

  return true;
};
