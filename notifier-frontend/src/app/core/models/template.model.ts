export type TemplateChannel = 'EMAIL' | 'SMS' | 'WEBSOCKET' | 'INAPP';

export interface Template {
  id: string;
  name: string;
  channel: TemplateChannel;
  subject: string;
  body: string;
  variables: string[];
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateTemplatePayload {
  name: string;
  channel: TemplateChannel;
  subject?: string;
  body: string;
  variables: string[];
}
