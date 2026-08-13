import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTableModule } from '@angular/material/table';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { DocumentInfo } from '../../../services/dashboard.service';

@Component({
  selector: 'app-documents-table',
  standalone: true,
  imports: [CommonModule, MatTableModule, MatProgressSpinnerModule],
  templateUrl: './documents-table.html',
  styleUrl: './documents-table.scss'
})
export class DocumentsTable {
  @Input() documents: DocumentInfo[] = [];
  @Input() processingDocs: { [key: string]: boolean } = {};
  @Input() isLoadingDocuments = false;

  @Output() refreshClicked = new EventEmitter<void>();
  @Output() uploadClicked = new EventEmitter<void>();
  @Output() processClicked = new EventEmitter<string>();
  @Output() viewResultClicked = new EventEmitter<string>();

  displayedColumns: string[] = ['filename', 'type', 'source', 'status', 'actions'];
}
