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
  
  protected get showNav(): boolean {
    return this.router.url !== '/login';
  }
}
