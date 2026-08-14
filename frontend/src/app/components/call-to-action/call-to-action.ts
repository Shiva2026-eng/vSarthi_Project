import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTableModule } from '@angular/material/table';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';

export interface DocumentWithCallToAction {
  document_id: string;
  document_type: string;
  summary: string;
  call_to_action: string;
}

export interface DocumentsResponse {
  status: boolean;
  message: string;
  documents: DocumentWithCallToAction[];
}
@Component({
  selector: 'app-call-to-action',
  standalone: true,
  imports: [CommonModule, MatTableModule],
  templateUrl: './call-to-action.html',
  styleUrl: './call-to-action.scss',
})
export class CallToAction implements OnInit {
  displayedColumns: string[] = ['document_id', 'document_type', 'summary', 'call_to_action'];
  recentCtas = signal<DocumentWithCallToAction[]>([]);
  private http = inject(HttpClient);
  fetchCtas() {
    return this.http
      .get<DocumentsResponse>(`${environment.baseUrl}/documents/call-to-actions`)
      .subscribe({
        next: (response) => {
          console.log(response);
          this.recentCtas.set(response.documents);
        },
        error: (e) => {
          console.log(e.error.detail);
        },
      });
  }
  ngOnInit() {
    this.fetchCtas();
  }
}
