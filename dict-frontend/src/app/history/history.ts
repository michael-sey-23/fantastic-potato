import { Component, inject, signal, OnInit, computed } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import {API_URL} from '../app.env';

@Component({
  selector: 'app-history',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './history.html',
  styleUrl: './history.css',
})
export class History implements OnInit {
  private http = inject(HttpClient);

  // Data Signals
  public records = signal<any[]>([]);
  public searchQuery = signal<string>('');
  public selectedRecord = signal<any | null>(null);

  // Filtering is derived state, so it updates automatically as records or query change.
  public filteredRecords = computed(() => {
    const query = this.searchQuery().toLowerCase();
    const allRecords = this.records();

    if (!query) return allRecords;

    return allRecords.filter(r =>
      r.query.toLowerCase().includes(query) ||
      r.response.toLowerCase().includes(query)
    );
  });

  ngOnInit(): void {
    this.refreshHistory();
  }

  protected onSearch(event: Event): void {
    const value = (event.target as HTMLInputElement).value;
    this.searchQuery.set(value);
  }

  protected selectRecord(record: any): void {
    this.selectedRecord.set(record);
  }

  refreshHistory(): void {
    this.http.get<any[]>(`${API_URL}acronyms/history`).subscribe({
      next: (data) => {
        // The backend already sorts history newest-first for the current user.
        this.records.set(data);
      },
      error: (err) => {
        console.error("Failed to load history:", err);
      }
    });
  }
}
