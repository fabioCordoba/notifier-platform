import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatDividerModule } from '@angular/material/divider';
import { NotificationService } from '../../../../core/services/notification.service';
import { Notification } from '../../../../core/models/notification.model';

@Component({
  selector: 'app-notification-detail',
  standalone: true,
  imports: [
    CommonModule, RouterLink, MatCardModule, MatButtonModule,
    MatIconModule, MatChipsModule, MatExpansionModule, MatDividerModule,
  ],
  templateUrl: './notification-detail.html',
  styleUrl: './notification-detail.scss',
})
export class NotificationDetailComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private notifService = inject(NotificationService);

  notification = signal<Notification | null>(null);
  loading = signal(true);

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id')!;
    this.notifService.getById(id).subscribe({
      next: n => { this.notification.set(n); this.loading.set(false); },
      error: () => this.loading.set(false),
    });
  }

  retry(): void {
    const n = this.notification();
    if (n) this.notifService.retry(n.id).subscribe(() => this.ngOnInit());
  }

  statusIcon(status: string): string {
    const map: Record<string, string> = {
      SENT: 'send', DELIVERED: 'done_all', FAILED: 'error',
      READ: 'mark_email_read', QUEUED: 'schedule', PROCESSING: 'sync',
    };
    return map[status] || 'help';
  }
}
