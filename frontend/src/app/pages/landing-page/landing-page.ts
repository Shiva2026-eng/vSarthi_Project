import { Component, inject, OnInit, signal } from '@angular/core';
import { Dashboard } from '../../components/LandingPage/dashboard/dashboard';
import { AuthService } from '../../services/auth-service';
import { HttpClient } from '@angular/common/http';
import { FileUploadModal } from '../../components/LandingPage/file-upload-modal/file-upload-modal';
import { DocumentsService } from '../../services/documents-service';
import { Router } from '@angular/router';
import { ConnectedAccounts } from '../../services/auth-service';
import { DatePipe } from '@angular/common';

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
  imports: [Dashboard, FileUploadModal, DatePipe],
  templateUrl: './landing-page.html',
  styleUrl: './landing-page.scss',
})
export class LandingPage implements OnInit {
  private http = inject(HttpClient);
  private auth_service = inject(AuthService);
  private documentsService = inject(DocumentsService);
  private router = inject(Router);

  documents = signal<Document[]>([]);
  processingDocIds = signal<Set<string>>(new Set());
  showModal: boolean = false;
  name = signal<string>('');
  email = signal<string>('');
  id = signal<string>('');
  created_at = signal<string>('');
  connected_accounts = signal<ConnectedAccounts>({
    outlook: false,
    telegram: false,
  });
  toggleModal() {
    this.showModal = !this.showModal;
  }

  ngOnInit(): void {
    if (!this.auth_service.isLoggedIn()) {
      this.auth_service.removeAccessToken();
      this.router.navigate(['/']);
      return;
    }
    this.fetchDocuments();
    this.auth_service.getUserInfo().subscribe({
      next: (user_info) => {
        this.name.set(user_info.details.name);
        this.connected_accounts.set(user_info.details.connected_accounts);
        this.created_at.set(user_info.details.created_at);
        this.id.set(user_info.details.id);
        this.email.set(user_info.details.email);
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.get('outlook_status') === 'success') {
          this.fetchOutlookEmails();
        }
      },
      error: (err) => {
        console.error('Failed to fetch user profile:', err);
      },
    });
  }

  isProcessing(doc: Document): boolean {
    return doc.processing_status === 'processing' || this.processingDocIds().has(doc.id);
  }

  sendForProcessing(document_id: string) {
    const currentSet = new Set(this.processingDocIds());
    currentSet.add(document_id);
    this.processingDocIds.set(currentSet);

    this.documents.update((docs) =>
      docs.map((d) => (d.id === document_id ? { ...d, processing_status: 'processing' } : d)),
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
        if (e?.status === 401 || e?.status === 403) {
          this.auth_service.removeAccessToken();
          this.router.navigate(['/']);
        } else {
          alert('Failed to process document. Please try again.');
          this.fetchDocuments();
        }
      },
    });
  }

  fetchDocuments(): void {
    this.http.get<Response>('http://127.0.0.1:8000/documents/get_all_documents').subscribe({
      next: (response) => {
        console.log('Fetched documents:', response);
        this.documents.set(response.data || []);
      },
      error: (e) => {
        console.error('Error fetching documents:', e);
        if (e?.status === 401 || e?.status === 403) {
          this.auth_service.removeAccessToken();
          this.router.navigate(['/']);
        }
      },
    });
  }

  showOutlookDrawer: boolean = false;
  outlookMessages = signal<any[]>([]);
  loadingOutlookMessages = signal<boolean>(false);
  ingestingMessageId: string | null = null;
  ingestingAllEmails: boolean = false;

  connectOutlook() {
    this.auth_service.getOutlookLoginUrl().subscribe({
      next: (res) => {
        if (res.auth_url) {
          window.location.href = res.auth_url;
        }
      },
      error: (err) => {
        console.error('Error fetching Outlook login URL:', err);
        alert('Failed to initiate Outlook connection.');
      },
    });
  }

  fetchOutlookEmails() {
    this.loadingOutlookMessages.set(true);
    this.auth_service.getOutlookMessages().subscribe({
      next: (res) => {
        console.log('fetching response...');
        this.loadingOutlookMessages.set(false);
        this.outlookMessages.set(res.messages || []);
        console.log('Response fetched...');
        this.showOutlookDrawer = true;
      },
      error: (err) => {
        this.loadingOutlookMessages.set(false);
        console.error('Error fetching Outlook messages:', err);
        alert('Failed to fetch Outlook emails. Make sure your account is connected.');
      },
    });
  }

  closeOutlookDrawer() {
    this.showOutlookDrawer = false;
  }

  importEmailBody(msg: any) {
    this.ingestingMessageId = msg.id;
    this.auth_service.ingestOutlookEmail(msg.id).subscribe({
      next: (res) => {
        this.ingestingMessageId = null;
        this.fetchDocuments();
        alert(res.message);
      },
      error: (err) => {
        this.ingestingMessageId = null;
        console.error('Error importing email body:', err);
        alert('Failed to import email body as document.');
      },
    });
  }

  importAllEmails() {
    this.ingestingAllEmails = true;
    this.auth_service.ingestAllOutlookEmails().subscribe({
      next: (res) => {
        this.ingestingAllEmails = false;
        this.fetchDocuments();
        this.closeOutlookDrawer();
        alert(res.message);
      },
      error: (err) => {
        this.ingestingAllEmails = false;
        console.error('Error importing all emails:', err);
        alert('Failed to import all emails.');
      },
    });
  }

  onFileUploaded(): void {
    this.fetchDocuments();
  }

  getSizeInKB(bytes: number): string {
    return (bytes / 1024).toFixed(2);
  }

  viewSummary(documentId: string) {
    this.documentsService.fetchProcessedDocument(documentId).subscribe({
      next: (response) => {
        console.log('Fetched summary:', response);
        this.router.navigate(['/summary']);
      },
      error: (e) => {
        console.error('Error fetching summary:', e);
        if (e?.status === 401 || e?.status === 403) {
          this.auth_service.removeAccessToken();
          this.router.navigate(['/']);
        }
      },
    });
  }
}
