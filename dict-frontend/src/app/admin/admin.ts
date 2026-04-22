import {Component, inject, OnInit, signal} from '@angular/core';
import {CommonModule} from '@angular/common';
import {HttpClient} from '@angular/common/http';
import {FormsModule, NgForm} from '@angular/forms';
import {Acronym} from '../models';
import {Observable} from 'rxjs';
import {shareReplay} from 'rxjs/operators';
import {API_URL} from '../app.env';

@Component({
  selector: 'app-admin',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './admin.html',
  styleUrl: './admin.css',
})
export class Admin implements OnInit {
  private http = inject(HttpClient);
  private apiUrl = `${API_URL}acronyms`;

  public suggestions: any[] = [];
  public selectedSuggestionIndex: number | null = null;
  public formData = { acronym: '', definition: '', description: '' };
  public acronyms$!: Observable<any[]>;
  public selectedAcronym: any | null = null;

  public isSubmitting = signal(false);
  public successMessage = signal<string | null>(null);
  public acronyms = signal<Acronym[]>([]);
  public visiblePopup = signal(false);

  ngOnInit() {
    this.fetchAcronyms();
    this.fetchSuggestions();
    // Cache the latest acronym list in a signal so the template can consume a plain array.
    this.acronyms$.subscribe({
      next: (res) => this.acronyms.set(res || []),
      error: (err) => console.error("Could not fetch acronyms", err)
    });
  }

  fetchAcronyms(): void {
    // shareReplay avoids duplicate network calls when the page binds to the same request more than once.
    this.acronyms$ = this.http.get<any[]>(`${this.apiUrl}/all-acronyms`).pipe(
      shareReplay({ bufferSize: 1, refCount: true })
    );
  }

  private refreshAcronyms(): void {
    this.fetchAcronyms();
    this.acronyms$.subscribe({
      next: (res) => this.acronyms.set(res || []),
      error: (err) => console.error("Could not fetch acronyms", err)
    });
  }

  fetchSuggestions(): void {
    this.http.get<any[]>(`${this.apiUrl}/suggestions`).subscribe({
      next: (res) => this.suggestions = res || [],
      error: (err) => console.error("Could not fetch suggestions", err)
    });
  }

  onReviewSuggestion(index: number, suggestion: any): void {
    this.selectedSuggestionIndex = index;
    this.formData.acronym = suggestion.acronym;
    this.formData.definition = '';
    this.formData.description = '';
  }

  onRejectSuggestion(index: number): void {
    this.http.delete(`${this.apiUrl}/suggestions/${index}`).subscribe({
      next: () => this.fetchSuggestions(),
      error: (err) => console.error("Failed to reject suggestion", err)
    });
  }

  onAddAcronym(form: NgForm): void {
    if (form.valid) {
      const data = form.value;
      this.isSubmitting.set(true);
      this.successMessage.set(null);

      this.http.post(`${this.apiUrl}/add`, data).subscribe({
        next: () => {
          this.successMessage.set(`Successfully added ${data.acronym}`);
          form.reset();

          if (this.selectedSuggestionIndex !== null) {
            // Once a suggestion becomes a real entry, remove it from the review queue.
            this.onRejectSuggestion(this.selectedSuggestionIndex);
            this.selectedSuggestionIndex = null;
          }

          this.isSubmitting.set(false);
          this.refreshAcronyms();
          setTimeout(() => this.successMessage.set(null), 3500);
        },
        error: (err) => {
          console.error("Admin action failed:", err);
          alert('Error: Action failed. Check your permissions.');
          this.isSubmitting.set(false);
        }
      });
    }
  }

  onClickAcronymCard(acronym: any): void {
    // The edit popup binds directly to the selected acronym object.
    this.selectedAcronym = acronym;
    this.visiblePopup.set(true);
  }

  onEditAcronym(form: NgForm): void {
    if (form.valid) {
      this.isSubmitting.set(true);
      this.http.put(`${this.apiUrl}/update`, this.selectedAcronym).subscribe({
        next: () => {
          this.successMessage.set(`Successfully updated ${this.selectedAcronym.acronym}`);
          this.visiblePopup.set(false);
          this.isSubmitting.set(false);
          this.refreshAcronyms();
          setTimeout(() => this.successMessage.set(null), 3500);
        },
        error: (err) => {
          console.error("Update failed:", err);
          alert('Error: Update failed. Check your permissions.');
          this.isSubmitting.set(false);
        }
      });
    }
  }

  onDeleteAcronym(): void {
    const acronym = this.selectedAcronym.acronym;
    this.http.delete(`${this.apiUrl}/delete/${acronym}`).subscribe({
      next: () => {
        this.successMessage.set(`Successfully deleted ${acronym}`);
        this.visiblePopup.set(false);
        this.selectedAcronym = null;
        this.refreshAcronyms();
        setTimeout(() => this.successMessage.set(null), 3500);
      },
      error: (err) => {
        console.error("Delete failed:", err);
        alert('Error: Delete failed. Check your permissions.');
      }
    });
  }
}
