import { inject, Injectable, Service } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { AuthService } from './auth-service';

@Service()
export class DocumentsService {
  private http = inject(HttpClient);
  private authService = inject(AuthService);

  uploadDocument(file: File) {
    const formdata = new FormData();
    formdata.append('file', file);
    return this.http.post('http://127.0.0.1:8000/documents/upload', formdata, {
      headers: {
        Authorization: `Bearer ${this.authService.getAccessToken()}`,
      },
    });
  }

  processDocument(documentId: string) {
    return this.http.post(
      `http://127.0.0.1:8000/documents/process_document/${documentId}`,
      {},
      {
        headers: {
          Authorization: `Bearer ${this.authService.getAccessToken()}`,
        },
      },
    );
  }
}
