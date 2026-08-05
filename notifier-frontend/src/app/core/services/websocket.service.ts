import { Injectable, OnDestroy, inject, signal } from '@angular/core';
import { Subject, Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { AuthService } from './auth.service';

export interface WsNotificationMessage {
  type: 'notification' | 'read_confirmed';
  data?: Record<string, unknown>;
  attempt_id?: string;
}

@Injectable({ providedIn: 'root' })
export class WebSocketService implements OnDestroy {
  private auth = inject(AuthService);
  private ws: WebSocket | null = null;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private messageSubject = new Subject<WsNotificationMessage>();
  readonly messages$: Observable<WsNotificationMessage> = this.messageSubject.asObservable();
  readonly connected = signal(false);

  connect(userId: string): void {
    const apiKey = this.auth.apiKey();
    if (!apiKey) return;
    const url = `${environment.wsUrl}/ws/notifications/?api_key=${apiKey}&user_id=${userId}`;
    this.ws = new WebSocket(url);

    this.ws.onopen = () => this.connected.set(true);

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as WsNotificationMessage;
        this.messageSubject.next(data);
      } catch {}
    };

    this.ws.onclose = () => {
      this.connected.set(false);
      this.reconnectTimer = setTimeout(() => this.connect(userId), 5000);
    };
  }

  markRead(attemptId: string): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ action: 'mark_read', attempt_id: attemptId }));
    }
  }

  disconnect(): void {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    this.ws?.close();
    this.connected.set(false);
  }

  ngOnDestroy(): void {
    this.disconnect();
  }
}
