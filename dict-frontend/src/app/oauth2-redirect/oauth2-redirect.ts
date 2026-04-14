import { Component, OnInit, inject } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { AuthService } from '../auth.service';

@Component({
  selector: 'app-oauth2-redirect',
  standalone: true,
  template: '<div class="loading-container"><h1>Finishing login...</h1></div>',
  styles: [`
    .loading-container {
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
      font-family: sans-serif;
    }
  `]
})
export class OAuth2Redirect implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private authService = inject(AuthService);

  ngOnInit() {
    const token = this.route.snapshot.queryParamMap.get('token');
    if (token) {
      localStorage.setItem('auth_token', token);
      this.authService.isLoggedIn.set(true);
      this.router.navigate(['/search']);
    } else {
      this.router.navigate(['/login']);
    }
  }
}
