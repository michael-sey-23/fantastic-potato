import { Injectable, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { ChatMessage } from './models';
import {API_URL} from './app.env';

@Injectable({
  providedIn: 'root',
})
export class ChatService {
  private http = inject(HttpClient);
  private router = inject(Router);

  public readonly chatHistory = signal<ChatMessage[]>([]);
  private messageIdCounter = 0;

  public sendQuestionToBot(question: string): void {
    if (!question.trim()) return;

    const now = new Date();
    const timestamp = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;

    const userMessage: ChatMessage = {
      id: this.messageIdCounter++,
      sender: 'user',
      text: question,
      timestamp: timestamp
    };

    this.chatHistory.update(history => [...history, userMessage]);

    this.http.get<any>(`${API_URL}acronyms/search?query=${question}`).subscribe({
      next: (data) => {
        const botMessage: ChatMessage = {
          id: this.messageIdCounter++,
          sender: 'bot',
          text: `${data[0]?.definition || 'No exact match found.'}`,
          timestamp: timestamp,
          category: data[0]?.category,
          url: data[0]?.url
        };

        this.chatHistory.update(history => [...history, botMessage]);
      },
      error: (err) => {
        if (err.status === 401 || err.status === 403) {
          localStorage.removeItem('auth_token');
          this.router.navigate(['/login']);
        } else {
          const errorMsg: ChatMessage = {
            id: this.messageIdCounter++,
            sender: 'bot',
            text: 'Error: Could not reach the server.',
            timestamp: timestamp,
            category: 'error'
          };
          this.chatHistory.update(history => [...history, errorMsg]);
        }
      }
    });
  }
}
