import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { FormsModule } from '@angular/forms';
import { NotificationService } from '../../../../core/services/notification.service';
import { Notification } from '../../../../core/models/notification.model';

@Component({
  selector: 'app-notifications-list',
  standalone: true,
  imports: [
    CommonModule, RouterLink, FormsModule,
    MatTableModule, MatButtonModule, MatIconModule,
    MatChipsModule, MatSelectModule, MatFormFieldModule,
  ],
  templateUrl: './notifications-list.html',
  styleUrl: './notifications-list.scss',
})
export class NotificationsListComponent implements OnInit {
  private notifService = inject(NotificationService);

  notifications = signal<Notification[]>([]);
  statusFilter = signal('');
  displayedColumns = ['title', 'priority', 'status', 'channels', 'recipients', 'created_at', 'actions'];

  statuses = ['', 'QUEUED', 'PROCESSING', 'COMPLETED', 'PARTIALLY_FAILED', 'FAILED', 'CANCELLED'];

  ngOnInit(): void { this.load(); }

  load(): void {
    this.notifService.list(this.statusFilter() || undefined).subscribe(res => {
      this.notifications.set(res.results);
    });
  }

  retry(id: string, event: Event): void {
    event.stopPropagation();
    this.notifService.retry(id).subscribe(() => this.load());
  }
}
