import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatDialogModule, MatDialog } from '@angular/material/dialog';
import { TemplateService } from '../../../../core/services/template.service';
import { Template } from '../../../../core/models/template.model';

@Component({
  selector: 'app-template-list',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatButtonModule, MatIconModule, MatChipsModule, MatDialogModule],
  templateUrl: './template-list.html',
  styleUrl: './template-list.scss',
})
export class TemplateListComponent implements OnInit {
  private templateService = inject(TemplateService);

  templates = signal<Template[]>([]);

  ngOnInit(): void {
    this.templateService.list().subscribe(res => this.templates.set(res.results));
  }

  delete(id: string): void {
    if (confirm('¿Eliminar plantilla?')) {
      this.templateService.delete(id).subscribe(() => this.ngOnInit());
    }
  }
}
