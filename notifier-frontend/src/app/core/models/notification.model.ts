export type NotificationPriority = 'LOW' | 'NORMAL' | 'HIGH' | 'CRITICAL';
export type NotificationStatus =
  | 'DRAFT' | 'QUEUED' | 'PROCESSING'
  | 'COMPLETED' | 'PARTIALLY_FAILED' | 'FAILED' | 'CANCELLED';
export type DeliveryChannel = 'EMAIL' | 'SMS' | 'WHATSAPP' | 'PUSH' | 'WEBSOCKET' | 'INAPP';
export type DeliveryStatus =
  | 'PENDING' | 'QUEUED' | 'PROCESSING' | 'SENT'
  | 'DELIVERED' | 'FAILED' | 'READ' | 'CANCELLED';

export interface DeliveryAttempt {
  id: string;
  channel: DeliveryChannel;
  provider: string;
  status: DeliveryStatus;
  error_message: string;
  attempt_number: number;
  sent_at: string | null;
  delivered_at: string | null;
  read_at: string | null;
  created_at: string;
}

export interface Recipient {
  id?: string;
  name: string;
  email: string;
  phone: string;
  app_user_id: string;
  push_token?: string;
  metadata?: Record<string, unknown>;
  delivery_attempts?: DeliveryAttempt[];
}

export interface Notification {
  id: string;
  title: string;
  message: string;
  priority: NotificationPriority;
  status: NotificationStatus;
  channels: DeliveryChannel[];
  template?: string;
  template_variables?: Record<string, string>;
  metadata?: Record<string, unknown>;
  scheduled_at: string | null;
  created_at: string;
  updated_at: string;
  total_recipients: number;
  delivered_count: number;
  recipients?: Recipient[];
}

export interface SendNotificationPayload {
  title: string;
  message?: string;
  template_id?: string;
  template_variables?: Record<string, string>;
  priority: NotificationPriority;
  channels: DeliveryChannel[];
  recipients: Omit<Recipient, 'id' | 'delivery_attempts'>[];
  scheduled_at?: string;
  metadata?: Record<string, unknown>;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
