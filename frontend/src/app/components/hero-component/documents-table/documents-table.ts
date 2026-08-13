import { Component, Input, Output, EventEmitter, OnChanges, SimpleChanges } from '@angular/core';
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
export class DocumentsTable implements OnChanges {
  @Input() documents: DocumentInfo[] = [];
  @Input() processingDocs: { [key: string]: boolean } = {};
  @Input() isLoadingDocuments = false;

  flattenedDocuments: (DocumentInfo & { isAttachment?: boolean, parentId?: string })[] = [];

  ngOnChanges(changes: SimpleChanges) {
    if (changes['documents']) {
      this.flattenedDocuments = [];
      for (const doc of this.documents) {
        this.flattenedDocuments.push(doc);
        if (doc.attachments && doc.attachments.length > 0) {
          for (const att of doc.attachments) {
            this.flattenedDocuments.push({ ...att, isAttachment: true, parentId: doc.id });
          }
        }
      }
    }
  }

  @Output() refreshClicked = new EventEmitter<void>();
  @Output() uploadClicked = new EventEmitter<void>();
  @Output() processClicked = new EventEmitter<string>();
  @Output() viewResultClicked = new EventEmitter<string>();

  displayedColumns: string[] = ['filename', 'type', 'source', 'status', 'actions'];
}
