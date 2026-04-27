export interface ChatMessage {
  id: number;
  sender: 'user' | 'bot'; // Who sent it?
  text: string;
  timestamp: string;
  category?: string; // Optional metadata from your backend
  url?: string; // Optional metadata
}

export interface Acronym {
  acronym: string
  definition: string
  description?: string
}

export interface Suggestion {
  acronym: string
  is_new_entry: boolean
}
