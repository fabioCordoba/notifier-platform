import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink } from '@angular/router';
import { ReactiveFormsModule, FormBuilder, Validators, FormArray } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatDividerModule } from '@angular/material/divider';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { NotificationService } from '../../../../core/services/notification.service';

@Component({
  selector: 'app-notification-send',
  standalone: true,
  imports: [
    CommonModule, RouterLink, ReactiveFormsModule,
    MatCardModule, MatButtonModule, MatIconModule, MatFormFieldModule,
    MatInputModule, MatSelectModule, MatCheckboxModule, MatDividerModule,
    MatProgressSpinnerModule,
  ],
  templateUrl: './notification-send.html',
  styleUrl: './notification-send.scss',
})
export class NotificationSendComponent {
  private fb = inject(FormBuilder);
  private notifService = inject(NotificationService);
  private router = inject(Router);

  sending = signal(false);
  error = signal('');

  channels = ['EMAIL', 'WEBSOCKET', 'INAPP', 'SMS', 'WHATSAPP', 'PUSH'];
  priorities = ['LOW', 'NORMAL', 'HIGH', 'CRITICAL'];

  form = this.fb.group({
    title: ['', Validators.required],
    message: [''],
    priority: ['NORMAL', Validators.required],
    channels: [['EMAIL'], Validators.required],
    scheduled_at: [null],
    recipients: this.fb.array([this.createRecipient()]),
  });

  get recipientsArray(): FormArray {
    return this.form.get('recipients') as FormArray;
  }

  createRecipient() {
    return this.fb.group({
      name: [''],
      email: [''],
      phone: [''],
      app_user_id: [''],
    });
  }

  addRecipient(): void {
    this.recipientsArray.push(this.createRecipient());
  }

  removeRecipient(index: number): void {
    if (this.recipientsArray.length > 1) this.recipientsArray.removeAt(index);
  }

  submit(): void {
    if (this.form.invalid) return;
    this.sending.set(true);
    this.error.set('');

    const value = this.form.value;
    const payload: any = {
      title: value.title,
      message: value.message || undefined,
      priority: value.priority,
      channels: value.channels,
      recipients: value.recipients,
      scheduled_at: value.scheduled_at || undefined,
    };

    this.notifService.send(payload).subscribe({
      next: n => this.router.navigate(['/notifications', n.id]),
      error: err => {
        this.error.set(err.error?.detail || 'Error al enviar la notificación.');
        this.sending.set(false);
      },
    });
  }
}
