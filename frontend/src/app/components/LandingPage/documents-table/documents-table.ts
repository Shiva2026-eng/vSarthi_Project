import { Component, EventEmitter, Input, Output, signal } from '@angular/core';
import { DatePipe } from '@angular/common';

export interface Document {
  created_at: string;
  extension: string;
  filename: string;
  id: string;
  mime_type: string;
  size: number;
  source: string;
  user_id: string;
  processing_status: string;
}

@Component({
  selector: 'app-documents-table',
  imports: [DatePipe],
  templateUrl: './documents-table.html',
  styleUrl: './documents-table.scss',
})
export class DocumentsTableComponent {
  @Input() documents = signal<Document[]>([]);
  @Input() processingDocIds = signal<Set<string>>(new Set());

  @Output() toggleModal = new EventEmitter<void>();
  @Output() sendForProcessing = new EventEmitter<string>();
  @Output() viewSummary = new EventEmitter<string>();

  isProcessing(doc: Document): boolean {
    return doc.processing_status === 'processing' || this.processingDocIds().has(doc.id);
  }

  getSizeInKB(bytes: number): string {
    return (bytes / 1024).toFixed(2);
  }

  onToggleModal() {
    this.toggleModal.emit();
  }

  onSendForProcessing(id: string) {
    this.sendForProcessing.emit(id);
  }

  onViewSummary(id: string) {
    this.viewSummary.emit(id);
  }
}
