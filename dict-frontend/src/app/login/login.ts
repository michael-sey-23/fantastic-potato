import { Component, inject, signal, ViewChild, ElementRef } from '@angular/core';
import { AuthService } from '../auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  templateUrl: './login.html',
  styleUrl: './login.css',
})
export class Login {
  public authService = inject(AuthService);
  
  // Track if we are in "Login" mode or "Sign Up" mode
  public isSignUpMode = signal(false);

  @ViewChild('usernameInput') usernameInput!: ElementRef<HTMLInputElement>;
  @ViewChild('passwordInput') passwordInput!: ElementRef<HTMLInputElement>;
  @ViewChild('confirmPasswordInput') confirmPasswordInput?: ElementRef<HTMLInputElement>;

  protected onToggleMode(): void {
    this.isSignUpMode.update(val => !val);
  }

  protected onSignIn(): void {
      this.authService.authError.set(null); // Clear previous errors

      const user = this.usernameInput.nativeElement.value;
      const pass = this.passwordInput.nativeElement.value;
      const confirmPass = this.confirmPasswordInput?.nativeElement.value;

      if (this.isSignUpMode()) {
        if (pass !== confirmPass) {
           this.authService.authError.set("Passwords do not match!");
           return;
        }
        if (!user || !pass) {
           this.authService.authError.set("Fields cannot be empty.");
           return;
        }

        // Handle Registration
        this.authService.register(user, pass).subscribe({
          next: () => {
             this.authService.authError.set(null);
             alert('Registration successful! You can now log in.');
             this.isSignUpMode.set(false);
          },
          error: (err) => {
             const apiError = typeof err.error === 'string' ? err.error : err.error?.message || 'Registration failed.';
             this.authService.authError.set(apiError);
          }
        });
      } else {
        // Handle Login
        this.authService.login(user, pass);
      }
  }
}
