import { Component, signal, inject } from '@angular/core';
import { Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { AuthService } from './auth.service';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  protected readonly title = signal('Dictionary Chatbot');
  protected authService = inject(AuthService);
  private router = inject(Router);
  
  constructor() {
    // Periodically check if the token has expired while the user is idle.
    setInterval(() => {
      if (this.authService.isLoggedIn()) {
        this.authService.checkAuth();
      }
    }, 60000); // Check every minute
  }

  protected get showNav(): boolean {
    // The login page is intentionally distraction-free, so the global nav is hidden there.
    return this.router.url !== '/login';
  }
}
