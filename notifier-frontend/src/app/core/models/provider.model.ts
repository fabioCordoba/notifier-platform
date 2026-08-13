export type ProviderChannel = 'EMAIL' | 'SMS' | 'WHATSAPP' | 'PUSH';
export type ProviderName = 'smtp' | 'sendgrid' | 'twilio' | 'firebase';

export interface Provider {
  id: string;
  channel: ProviderChannel;
  name: ProviderName;
  is_default: boolean;
  is_active: boolean;
  created_at: string;
}

export interface ProviderPayload {
  channel: ProviderChannel;
  name: ProviderName;
  is_default: boolean;
  is_active?: boolean;
  config: Record<string, unknown>;
}
