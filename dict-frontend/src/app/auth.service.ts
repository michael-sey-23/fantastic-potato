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

  private tokenSignal = signal<string | null>(localStorage.getItem('auth_token'));

  public readonly isLoggedIn = computed(() => !!this.tokenSignal());

  public readonly isTokenExpired = computed(() => {
    const token = this.tokenSignal();
    if (!token) return true;
    const decoded = this.decodeToken(token);
    if (!decoded || !decoded.exp) return true;
    return decoded.exp < Date.now() / 1000;
  });

  public readonly isAdmin = computed(() => {
    return this.isLoggedIn() && this.getRole() === 'ROLE_ADMIN';
  });
  public readonly authError = signal<string | null>(null);

  public login(username: string, password: string) {
    this.authError.set(null); // Clear previous errors
    const body = { username, password };

    return this.http.post<{ token: string }>(`${this.baseUrl}/login`, body).subscribe({
      next: (response) => {
        this.handleLoginSuccess(response.token);
        // Successful login always lands on the main search experience.
        this.router.navigate(['/search']);
      },
      error: (err) => {
        this.authError.set('Invalid username or password.');
      }
    });
  }

  public logout(): void {
    localStorage.removeItem('auth_token');
    this.tokenSignal.set(null);
    this.router.navigate(['/login']);
  }

  public register(username: string, password: string) {
    return this.http.post(`${this.baseUrl}/register`, { username, password });
  }

  private decodeToken(token: string): any {
    try {
      // JWT payloads use URL-safe base64, so they need to be normalized before decoding.
      const payloadBase64 = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
      const decodedJson = atob(payloadBase64);
      return JSON.parse(decodedJson);
    } catch (e) {
      console.error("Token decoding failed:", e);
      return null;
    }
  }

  public getRole(): string | null {
    const token = this.tokenSignal();
    if (!token) return null;
    const decoded = this.decodeToken(token);
    // Role is embedded in the JWT by the Spring backend during login.
    return decoded?.role || null;
  }

  public checkAuth(): boolean {
    if (this.isTokenExpired()) {
      this.logout();
      return false;
    }
    return true;
  }

  public handleLoginSuccess(token: string) {
    localStorage.setItem('auth_token', token);
    this.tokenSignal.set(token);
  }

}
