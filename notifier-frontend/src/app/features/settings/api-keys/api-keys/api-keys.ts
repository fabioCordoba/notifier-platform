import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatTableModule } from '@angular/material/table';
import { AuthService } from '../../../../core/services/auth.service';
import { environment } from '../../../../../environments/environment';

interface ApiKeyItem {
  id: string;
  name: string;
  key_prefix: string;
  is_active: boolean;
  last_used_at: string | null;
  created_at: string;
}

@Component({
  selector: 'app-api-keys',
  standalone: true,
  imports: [
    CommonModule, ReactiveFormsModule,
    MatCardModule, MatButtonModule, MatIconModule,
    MatFormFieldModule, MatInputModule, MatSnackBarModule, MatTableModule,
  ],
  templateUrl: './api-keys.html',
  styleUrl: './api-keys.scss',
})
export class ApiKeysComponent implements OnInit {
  private http = inject(HttpClient);
  protected auth = inject(AuthService);
  private fb = inject(FormBuilder);
  private snack = inject(MatSnackBar);

  keys = signal<ApiKeyItem[]>([]);
  newKey = signal<string | null>(null);
  displayedColumns = ['prefix', 'name', 'last_used_at', 'created_at', 'actions'];

  form = this.fb.group({ name: ['', Validators.required] });
  connectForm = this.fb.group({ api_key: ['', Validators.required] });

  ngOnInit(): void { this.load(); }

  load(): void {
    this.http.get<ApiKeyItem[]>(`${environment.apiUrl}/api/v1/auth/api-keys/`).subscribe({
      next: keys => this.keys.set(keys),
    });
  }

  create(): void {
    if (this.form.invalid) return;
    this.http.post<{ key: string; name: string; prefix: string; id: string }>(
      `${environment.apiUrl}/api/v1/auth/api-keys/create/`,
      { name: this.form.value.name }
    ).subscribe(res => {
      this.newKey.set(res.key);
      this.form.reset();
      this.load();
    });
  }

  revoke(id: string): void {
    if (!confirm('¿Revocar esta API Key?')) return;
    this.http.delete(`${environment.apiUrl}/api/v1/auth/api-keys/${id}/revoke/`).subscribe(() => this.load());
  }

  setActiveKey(): void {
    const key = this.connectForm.value.api_key;
    if (key) {
      this.auth.setApiKey(key);
      this.snack.open('API Key guardada', 'OK', { duration: 3000 });
    }
  }

  copyToClipboard(text: string): void {
    navigator.clipboard.writeText(text);
    this.snack.open('Copiado al portapapeles', '', { duration: 2000 });
  }
}
