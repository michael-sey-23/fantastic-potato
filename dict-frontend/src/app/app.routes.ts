import { Routes } from '@angular/router';
import { Search } from './search/search';
import { Admin } from './admin/admin';
import { History } from './history/history';
import { Login } from './login/login';
import { authGuard } from './auth-guard';
import { isLoggedInGuard } from './is-logged-in-guard';

export const routes: Routes = [
  { path: 'search', component: Search, canActivate: [isLoggedInGuard] },
  { path: 'admin', component: Admin, canActivate: [isLoggedInGuard, authGuard] },
  { path: 'history', component: History, canActivate: [isLoggedInGuard] },
  { path: 'login', component: Login},
  { path: '', redirectTo: 'search', pathMatch: 'full' }
];