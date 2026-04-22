import {Component, inject, signal, OnInit} from '@angular/core';
import {ChatService} from '../chat-service';
import {Acronym} from '../models';
import {shareReplay} from 'rxjs/operators';
import {Observable} from 'rxjs';
import {HttpClient} from '@angular/common/http';
import {API_URL} from '../app.env';


@Component({
  selector: 'app-search',
  imports: [],
  templateUrl: './search.html',
  styleUrl: './search.css',
})
export class Search implements OnInit {
  // Exposed publicly because the template renders directly from the service signals.
  public acronymService = inject(ChatService)
  public acronyms = signal<Acronym[]>([]);
  public selectedAcronym: any | null = null;
  public visiblePopup = signal(false);
  public acronyms$!: Observable<any[]>;
  private http = inject(HttpClient);
  private apiUrl = `${API_URL}acronyms`

  ngOnInit() {
    this.fetchAcronyms();
    // Subscribe once to populate the signal the template reads from
    this.acronyms$.subscribe({
      next: (res) => this.acronyms.set(res || []),
      error: (err) => console.error("Could not fetch acronyms", err)
    });
  }

  protected performSearch(text: string): void {
    // Search state is owned by ChatService so the conversation survives within the route.
    this.acronymService.sendQuestionToBot(text);
    console.log(`"${text}" was searched for`)
  }

  onClickAcronymCard(acronym: any): void {
    // The edit popup binds directly to the selected acronym object.
    this.selectedAcronym = acronym;
    this.visiblePopup.set(true);
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
}
