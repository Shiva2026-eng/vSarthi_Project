import { Component, inject, Input } from '@angular/core';
import { DocumentsService } from '../../../services/documents-service';
import { Router } from '@angular/router';

export interface ProcessedDocument {
  id: string;
  document_id: string;
  document_type: string;
  summary: string;
  extracted_text: string;
  structured_data: StructuredData;
  processed_at: string;
}

export interface StructuredData {
  document_type: string;
  title: string;
  summary: string;
  keywords: string[];
}

@Component({
  selector: 'app-summarised-document',
  imports: [],
  templateUrl: './summarised-document.html',
  styleUrl: './summarised-document.scss',
})
export class SummarisedDocument {
  @Input() document?: ProcessedDocument;
  private documentsService = inject(DocumentsService);
  private router = inject(Router);

  get doc(): ProcessedDocument | null {
    return this.document || this.documentsService.currentProcessedDocument();
  }

  goBack() {
    this.router.navigate(['/dashboard']);
  }
}

