import { Injectable, signal, inject, computed } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { API_URL} from './app.env';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private http = inject(HttpClient);
  private router = inject(Router);
  private readonly baseUrl = `${API_URL}auth`;

  // Initialize signals based on storage
  public readonly isLoggedIn = signal(!!localStorage.getItem('auth_token'));

  public readonly isAdmin = computed(() => {
    return this.isLoggedIn() && this.getRole() === 'ROLE_ADMIN';
  });
  public readonly authError = signal<string | null>(null);

  public login(username: string, password: string) {
    this.authError.set(null); // Clear previous errors
    const body = { username, password };

    return this.http.post<{ token: string }>(`${this.baseUrl}/login`, body).subscribe({
      next: (response) => {
        const token = response.token;
        localStorage.setItem('auth_token', token);
        this.isLoggedIn.set(true);
        this.router.navigate(['/search']);
      },
      error: (err) => {
        this.authError.set('Invalid username or password.');
      }
    });
  }

  public logout(): void {
    localStorage.removeItem('auth_token');
    this.isLoggedIn.set(false);
    this.router.navigate(['/login']);
  }

  public register(username: string, password: string) {
    return this.http.post(`${this.baseUrl}/register`, { username, password });
  }

  private decodeToken(token: string): any {
    try {
      const payloadBase64 = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
      const decodedJson = atob(payloadBase64);
      return JSON.parse(decodedJson);
    } catch (e) {
      console.error("Token decoding failed:", e);
      return null;
    }
  }

  public getRole(): string | null {
    const token = localStorage.getItem('auth_token');
    if (!token) return null;
    const decoded = this.decodeToken(token);
    return decoded?.role || null;
  }
}
