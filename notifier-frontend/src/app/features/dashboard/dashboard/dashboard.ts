import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { NotificationService } from '../../../core/services/notification.service';
import { Notification } from '../../../core/models/notification.model';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink, MatCardModule, MatButtonModule, MatIconModule, MatChipsModule],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.scss',
})
export class DashboardComponent implements OnInit {
  private notifService = inject(NotificationService);

  total = signal(0);
  completed = signal(0);
  failed = signal(0);
  recentNotifications = signal<Notification[]>([]);

  ngOnInit(): void {
    this.notifService.list().subscribe(res => {
      this.total.set(res.count);
      this.recentNotifications.set(res.results.slice(0, 10));
      this.completed.set(res.results.filter(n => n.status === 'COMPLETED').length);
      this.failed.set(res.results.filter(n => n.status === 'FAILED').length);
    });
  }

  statusColor(status: string): string {
    const map: Record<string, string> = {
      COMPLETED: 'primary', FAILED: 'warn', PARTIALLY_FAILED: 'accent',
      QUEUED: 'accent', PROCESSING: 'accent',
    };
    return map[status] || '';
  }
}
