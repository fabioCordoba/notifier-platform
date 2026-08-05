import { TestBed, fakeAsync, tick } from '@angular/core/testing';
import { WebSocketService, WsNotificationMessage } from './websocket.service';
import { AuthService } from './auth.service';
import { environment } from '../../../environments/environment';

class MockWebSocket {
  static OPEN = 1;
  readyState = MockWebSocket.OPEN;
  url: string;
  onopen: (() => void) | null = null;
  onmessage: ((event: { data: string }) => void) | null = null;
  onclose: (() => void) | null = null;
  sentMessages: string[] = [];

  constructor(url: string) {
    this.url = url;
  }

  send(data: string): void {
    this.sentMessages.push(data);
  }

  close(): void {
    this.onclose?.();
  }

  triggerOpen(): void {
    this.onopen?.();
  }

  triggerMessage(data: unknown): void {
    this.onmessage?.({ data: JSON.stringify(data) });
  }

  triggerClose(): void {
    this.onclose?.();
  }
}

describe('WebSocketService', () => {
  let service: WebSocketService;
  let authService: AuthService;
  let mockWs: MockWebSocket;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    authService = TestBed.inject(AuthService);
    authService.setApiKey('ntf_testkey');

    spyOn(window, 'WebSocket' as never).and.callFake((url: string) => {
      mockWs = new MockWebSocket(url);
      return mockWs as unknown as WebSocket;
    });

    service = TestBed.inject(WebSocketService);
  });

  afterEach(() => {
    service.disconnect();
    authService.clearApiKey();
    localStorage.removeItem('notifier_api_key');
  });

  it('connect() creates WebSocket with correct URL including api_key and user_id', () => {
    service.connect('user-42');
    const expectedUrl = `${environment.wsUrl}/ws/notifications/?api_key=ntf_testkey&user_id=user-42`;
    expect(mockWs.url).toBe(expectedUrl);
  });

  it('sets connected signal to true when WebSocket opens', () => {
    service.connect('user-42');
    expect(service.connected()).toBeFalse();
    mockWs.triggerOpen();
    expect(service.connected()).toBeTrue();
  });

  it('emits received messages on messages$', () => {
    const received: WsNotificationMessage[] = [];
    service.messages$.subscribe((msg) => received.push(msg));

    service.connect('user-42');
    const payload: WsNotificationMessage = { type: 'notification', data: { title: 'Hi' } };
    mockWs.triggerMessage(payload);

    expect(received.length).toBe(1);
    expect(received[0].type).toBe('notification');
  });

  it('markRead() sends correct JSON when connection is open', () => {
    service.connect('user-42');

    service.markRead('attempt-99');

    expect(mockWs.sentMessages.length).toBe(1);
    expect(JSON.parse(mockWs.sentMessages[0])).toEqual({
      action: 'mark_read',
      attempt_id: 'attempt-99',
    });
  });

  it('reconnects automatically after connection closes', fakeAsync(() => {
    service.connect('user-42');
    mockWs.triggerOpen();
    expect(service.connected()).toBeTrue();

    const firstWs = mockWs;
    firstWs.triggerClose();
    expect(service.connected()).toBeFalse();

    tick(5000);
    expect(mockWs).not.toBe(firstWs);
  }));

  it('does not connect when API key is absent', () => {
    authService.clearApiKey();
    service.connect('user-42');
    expect(window.WebSocket as unknown as jasmine.Spy).not.toHaveBeenCalled();
  });

  it('disconnect() clears the connected signal', () => {
    service.connect('user-42');
    mockWs.triggerOpen();
    expect(service.connected()).toBeTrue();

    service.disconnect();
    expect(service.connected()).toBeFalse();
  });
});
