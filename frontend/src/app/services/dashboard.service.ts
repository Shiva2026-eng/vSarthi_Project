import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';

export interface DocumentInfo {
  id: string;
  filename: string;
  extension: string;
  mime_type: string;
  size: number;
  source: string;
  processing_status: string;
  created_at: string;
}

export interface UserProfile {
  id: string;
  username: string;
  email: string;
  name: string;
  connected_account?: {
    outlook?: boolean;
  };
}

export interface ProcessedDocumentResult {
  id: string;
  document_id: string;
  document_type: string;
  summary: string;
  extracted_text: string;
  structured_data: any;
  processed_at: string;
}

export interface DashboardInfo {
  totalDocuments: number;
  processingDocuments: number;
  completedDocuments: number;
}

@Injectable({
  providedIn: 'root'
})
export class DashboardService {
  private http = inject(HttpClient);
  private baseUrl = environment.baseUrl;

  getUserProfile() {
    return this.http.get<{ success: boolean; details: UserProfile }>(`${this.baseUrl}/user/my_profile`);
  }

  getDocuments() {
    return this.http.get<{ success: boolean; message: string; data: DocumentInfo[] }>(`${this.baseUrl}/documents/get_all_documents`);
  }

  uploadDocument(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post<{ success: boolean; message: string; data: any }>(`${this.baseUrl}/documents/upload`, formData);
  }

  connectOutlook() {
    return this.http.get<{ success: boolean; auth_url: string }>(`${this.baseUrl}/user/connect-account/outlook/login`);
  }

  fetchOutlookEmails() {
    return this.http.post<{ success: boolean; message: string; count: number }>(`${this.baseUrl}/user/outlook/ingest-all-emails`, {});
  }

  processDocument(documentId: string) {
    return this.http.post<{ success: boolean; message: string; data: any }>(`${this.baseUrl}/documents/process_document/${documentId}`, {});
  }

  getDocumentResult(documentId: string) {
    return this.http.get<ProcessedDocumentResult>(`${this.baseUrl}/documents/document/${documentId}`);
  }
}
