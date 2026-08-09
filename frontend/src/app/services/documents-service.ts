import { inject, Injectable, Service, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { AuthService } from './auth-service';
import { ProcessedDocument } from '../components/LandingPage/summarised-document/summarised-document';
import { tap } from 'rxjs';

@Service()
export class DocumentsService {
  private http = inject(HttpClient);
  private authService = inject(AuthService);
  currentProcessedDocument = signal<ProcessedDocument | null>(null);

  uploadDocument(file: File) {
    const formdata = new FormData();
    formdata.append('file', file);
    return this.http.post('http://127.0.0.1:8000/documents/upload', formdata);
  }

  processDocument(documentId: string) {
    return this.http.post(
      `http://127.0.0.1:8000/documents/process_document/${documentId}`,
      {},
    );
  }

  fetchProcessedDocument(documentId: string) {
    return this.http
      .get<ProcessedDocument>(
        `http://127.0.0.1:8000/documents/document/${documentId}`,
      )
      .pipe(
        tap((data) => {
          this.currentProcessedDocument.set(data);
        }),
      );
  }
}

