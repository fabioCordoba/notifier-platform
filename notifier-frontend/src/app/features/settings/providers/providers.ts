import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatTableModule } from '@angular/material/table';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { ProviderService } from '../../../core/services/provider.service';
import { Provider, ProviderChannel, ProviderName } from '../../../core/models/provider.model';

const CONFIG_TEMPLATES: Record<string, Record<string, unknown>> = {
  smtp: {
    EMAIL_HOST: '', EMAIL_PORT: 465, EMAIL_USE_TLS: false, EMAIL_USE_SSL: true,
    EMAIL_HOST_USER: '', EMAIL_HOST_PASSWORD: '', DEFAULT_FROM_EMAIL: '',
  },
  sendgrid: { api_key: '', DEFAULT_FROM_EMAIL: '' },
  twilio: { TWILIO_ACCOUNT_SID: '', TWILIO_AUTH_TOKEN: '', TWILIO_FROM_NUMBER: '' },
  firebase: {
    type: 'service_account', project_id: '', private_key_id: '',
    private_key: '', client_email: '', client_id: '',
  },
  chatwoot: {
    CHATWOOT_BASE_URL: 'https://app.chatwoot.com',
    CHATWOOT_ACCOUNT_ID: '',
    CHATWOOT_INBOX_ID: '',
    CHATWOOT_API_TOKEN: '',
  },
};

const CHANNEL_PROVIDERS: Record<ProviderChannel, ProviderName[]> = {
  EMAIL:    ['smtp', 'sendgrid'],
  SMS:      ['twilio'],
  WHATSAPP: ['twilio', 'chatwoot'],
  PUSH:     ['firebase'],
};

@Component({
  selector: 'app-providers',
  standalone: true,
  imports: [
    CommonModule, ReactiveFormsModule,
    MatButtonModule, MatIconModule, MatFormFieldModule,
    MatInputModule, MatSelectModule, MatTableModule, MatSlideToggleModule,
  ],
  templateUrl: './providers.html',
  styleUrl: './providers.scss',
})
export class ProvidersComponent implements OnInit {
  private fb = inject(FormBuilder);
  private svc = inject(ProviderService);

  providers = signal<Provider[]>([]);
  showForm = signal(false);
  saving = signal(false);
  error = signal('');
  configError = signal('');

  channels: ProviderChannel[] = ['EMAIL', 'SMS', 'WHATSAPP', 'PUSH'];
  displayedColumns = ['channel', 'name', 'is_default', 'is_active', 'created_at', 'actions'];

  form = this.fb.group({
    channel:    ['EMAIL' as ProviderChannel, Validators.required],
    name:       ['smtp' as ProviderName,     Validators.required],
    is_default: [true],
    config_raw: ['', Validators.required],
  });

  get availableProviders(): ProviderName[] {
    const ch = this.form.value.channel as ProviderChannel;
    return CHANNEL_PROVIDERS[ch] || [];
  }

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.svc.list().subscribe(list => this.providers.set(list));
  }

  onChannelChange(): void {
    const providers = this.availableProviders;
    this.form.patchValue({ name: providers[0] });
    this.fillTemplate();
  }

  fillTemplate(): void {
    const name = this.form.value.name as ProviderName;
    const tpl = CONFIG_TEMPLATES[name] ?? {};
    this.form.patchValue({ config_raw: JSON.stringify(tpl, null, 2) });
    this.configError.set('');
  }

  parseConfig(): Record<string, unknown> | null {
    try {
      const parsed = JSON.parse(this.form.value.config_raw ?? '{}');
      this.configError.set('');
      return parsed;
    } catch {
      this.configError.set('JSON inválido — revisa la sintaxis.');
      return null;
    }
  }

  save(): void {
    const config = this.parseConfig();
    if (!config || this.form.invalid) return;
    this.saving.set(true);
    this.error.set('');

    const payload = {
      channel:    this.form.value.channel as ProviderChannel,
      name:       this.form.value.name as ProviderName,
      is_default: !!this.form.value.is_default,
      config,
    };

    this.svc.create(payload).subscribe({
      next: () => {
        this.load();
        this.showForm.set(false);
        this.form.reset({ channel: 'EMAIL', name: 'smtp', is_default: true, config_raw: '' });
        this.saving.set(false);
      },
      error: err => {
        this.error.set(err.error?.detail || JSON.stringify(err.error) || 'Error al guardar.');
        this.saving.set(false);
      },
    });
  }

  remove(id: string): void {
    if (!confirm('¿Eliminar este provider?')) return;
    this.svc.remove(id).subscribe(() => this.load());
  }
}
