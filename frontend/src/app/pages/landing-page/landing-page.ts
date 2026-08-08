import { Component, inject, OnInit, signal } from '@angular/core';
import { Dashboard } from '../../components/LandingPage/dashboard/dashboard';
import { SectionBanner } from '../../components/LandingPage/section-banner/section-banner';
import { AuthService } from '../../services/auth-service';
import { HttpClient } from '@angular/common/http';
import { FileUploadModal } from '../../components/LandingPage/file-upload-modal/file-upload-modal';
import { DocumentsService } from '../../services/documents-service';

interface Response {
  data: Document[];
  success: boolean;
  message: string;
}

interface Document {
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
  selector: 'app-landing-page',
  imports: [Dashboard, SectionBanner, FileUploadModal],
  templateUrl: './landing-page.html',
  styleUrl: './landing-page.scss',
})
export class LandingPage implements OnInit {
  private http = inject(HttpClient);
  private auth_service = inject(AuthService);
  private documentsService = inject(DocumentsService);

  documents = signal<Document[]>([]);
  processingDocIds = signal<Set<string>>(new Set());
  showModal: boolean = false;

  toggleModal() {
    this.showModal = !this.showModal;
  }

  ngOnInit(): void {
    this.fetchDocuments();
  }

  isProcessing(doc: Document): boolean {
    return (
      doc.processing_status === 'processing' ||
      this.processingDocIds().has(doc.id)
    );
  }

  sendForProcessing(document_id: string) {
    const currentSet = new Set(this.processingDocIds());
    currentSet.add(document_id);
    this.processingDocIds.set(currentSet);

    this.documents.update((docs) =>
      docs.map((d) =>
        d.id === document_id ? { ...d, processing_status: 'processing' } : d
      )
    );

    this.documentsService.processDocument(document_id).subscribe({
      next: (response) => {
        console.log('Document processed successfully:', response);
        const updatedSet = new Set(this.processingDocIds());
        updatedSet.delete(document_id);
        this.processingDocIds.set(updatedSet);
        this.fetchDocuments();
      },
      error: (e) => {
        console.error('Error processing document:', e);
        const updatedSet = new Set(this.processingDocIds());
        updatedSet.delete(document_id);
        this.processingDocIds.set(updatedSet);
        alert('Failed to process document. Please try again.');
        this.fetchDocuments();
      },
    });
  }

  fetchDocuments(): void {
    this.http
      .get<Response>('http://127.0.0.1:8000/documents/get_all_documents', {
        headers: {
          Authorization: `Bearer ${this.auth_service.getAccessToken()}`,
        },
      })
      .subscribe({
        next: (response) => {
          console.log('Fetched documents:', response);
          this.documents.set(response.data);
        },
        error: (e) => {
          console.error('Error fetching documents:', e);
        },
      });
  }

  onFileUploaded(): void {
    this.fetchDocuments();
  }

  getSizeInKB(bytes: number): string {
    return (bytes / 1024).toFixed(2);
  }
}

