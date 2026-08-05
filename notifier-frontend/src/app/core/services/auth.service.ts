import { Injectable, signal } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class AuthService {
  readonly apiKey = signal<string | null>(localStorage.getItem('notifier_api_key'));

  setApiKey(key: string): void {
    localStorage.setItem('notifier_api_key', key);
    this.apiKey.set(key);
  }

  clearApiKey(): void {
    localStorage.removeItem('notifier_api_key');
    this.apiKey.set(null);
  }

  isAuthenticated(): boolean {
    return !!this.apiKey();
  }
}
