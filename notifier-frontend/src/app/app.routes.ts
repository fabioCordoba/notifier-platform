import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () => import('./layout/shell/shell').then(m => m.ShellComponent),
    children: [
      { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
      {
        path: 'dashboard',
        loadComponent: () => import('./features/dashboard/dashboard/dashboard').then(m => m.DashboardComponent),
      },
      {
        path: 'notifications',
        loadComponent: () => import('./features/notifications/list/notifications-list/notifications-list').then(m => m.NotificationsListComponent),
      },
      {
        path: 'notifications/send',
        loadComponent: () => import('./features/notifications/send/notification-send/notification-send').then(m => m.NotificationSendComponent),
      },
      {
        path: 'notifications/:id',
        loadComponent: () => import('./features/notifications/detail/notification-detail/notification-detail').then(m => m.NotificationDetailComponent),
      },
      {
        path: 'templates',
        loadComponent: () => import('./features/templates/list/template-list/template-list').then(m => m.TemplateListComponent),
      },
      {
        path: 'settings/api-keys',
        loadComponent: () => import('./features/settings/api-keys/api-keys/api-keys').then(m => m.ApiKeysComponent),
      },
    ],
  },
];
