import { inject, Inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from './auth.service';

export const authGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  // 🛡️ Double Check: Are they an admin?
  if (authService.isLoggedIn() && authService.getRole() === 'ROLE_ADMIN') {
    return true;
  }

  // If not admin, kick them back to search!
  console.warn('Unauthorized Access Attempted!');
  router.navigate(['/search']);
  return false;
};

