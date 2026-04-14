import { Component, inject, signal, computed } from '@angular/core';
import { ChatService } from '../chat-service';


@Component({
  selector: 'app-search',
  imports: [],
  templateUrl: './search.html',
  styleUrl: './search.css',
})
export class Search {
  // We make this public so the HTML template can read the searchResults directly!
  public acronymService = inject(ChatService)
  
  protected performSearch(text: string): void {
    // Forward the text to the backend
    this.acronymService.sendQuestionToBot(text);
    console.log(`"${text}" was searched for`)
  }
}
