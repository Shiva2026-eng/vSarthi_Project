import { Component, OnInit, inject, signal, computed, ViewEncapsulation } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import {
  DashboardService,
  UserProfile,
  DocumentInfo,
  ProcessedDocumentResult,
} from '../../services/dashboard.service';
import { AuthService } from '../../services/auth-service';
import { finalize } from 'rxjs/operators';
import { FormsModule } from '@angular/forms';
import { Sidebar } from './sidebar/sidebar';
import { DashboardStats } from './dashboard-stats/dashboard-stats';
import { DocumentsTable } from './documents-table/documents-table';
import { UploadModal } from './upload-modal/upload-modal';
import { ResultModal } from './result-modal/result-modal';

@Component({
  selector: 'app-hero-component',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    Sidebar,
    DashboardStats,
    DocumentsTable,
    UploadModal,
    ResultModal,
    RouterModule
  ],
  templateUrl: './hero-component.html',
  styleUrl: './hero-component.scss',
  encapsulation: ViewEncapsulation.None,
})
export class HeroComponent implements OnInit {
  private dashboardService = inject(DashboardService);
  private authService = inject(AuthService);
  private route = inject(ActivatedRoute);
  private router = inject(Router);

  // State Signals
  userProfile = signal<UserProfile | null>(null);
  documents = signal<DocumentInfo[]>([]);
  isLoadingProfile = signal<boolean>(true);
  isLoadingDocuments = signal<boolean>(true);
  isUploading = signal<boolean>(false);
  isFetchingEmails = signal<boolean>(false);

  // Modal State
  isUploadModalOpen = signal<boolean>(false);
  selectedFile = signal<File | null>(null);

  isResultModalOpen = signal<boolean>(false);
  selectedResult = signal<ProcessedDocumentResult | null>(null);
  isLoadingResult = signal<boolean>(false);

  // Processing tracking
  processingDocs = signal<{ [key: string]: boolean }>({});

  // Table configuration
  displayedColumns: string[] = ['filename', 'type', 'source', 'status', 'actions'];

  // Derived Dashboard Stats
  totalDocuments = computed(() => this.documents().length);
  processingDocuments = computed(
    () =>
      this.documents().filter(
        (d) => d.processing_status === 'pending' || d.processing_status === 'processing',
      ).length,
  );
  completedDocuments = computed(
    () => this.documents().filter((d) => d.processing_status === 'completed').length,
  );

  // Error State
  errorMessage = signal<string | null>(null);

  ngOnInit() {
    this.checkOutlookCallback();
    this.fetchUserProfile();
    this.fetchDocuments();
  }

  private checkOutlookCallback() {
    this.route.queryParams.subscribe((params) => {
      if (params['outlook_status'] === 'success') {
        // Outlook connected successfully, refresh profile
        this.fetchUserProfile();
      }
    });
  }

  fetchUserProfile() {
    this.isLoadingProfile.set(true);
    this.dashboardService
      .getUserProfile()
      .pipe(finalize(() => this.isLoadingProfile.set(false)))
      .subscribe({
        next: (res) => {
          if (res.success) {
            this.userProfile.set(res.details);
          }
        },
        error: (err) => {
          this.errorMessage.set('Failed to load user profile.');
          console.error(err);
        },
      });
  }

  fetchDocuments() {
    this.isLoadingDocuments.set(true);
    this.dashboardService
      .getDocuments()
      .pipe(finalize(() => this.isLoadingDocuments.set(false)))
      .subscribe({
        next: (res) => {
          if (res.success) {
            this.documents.set(res.data || []);
          }
        },
        error: (err) => {
          this.errorMessage.set('Failed to load documents.');
          console.error(err);
        },
      });
  }

  // Outlook Actions
  connectOutlook() {
    this.dashboardService.connectOutlook().subscribe({
      next: (res) => {
        if (res.success && res.auth_url) {
          window.location.href = res.auth_url; // Redirect to Microsoft OAuth
        }
      },
      error: (err) => {
        this.errorMessage.set('Failed to initiate Outlook connection.');
        console.error(err);
      },
    });
  }

  fetchOutlookEmails() {
    this.isFetchingEmails.set(true);
    this.dashboardService
      .fetchOutlookEmails()
      .pipe(finalize(() => this.isFetchingEmails.set(false)))
      .subscribe({
        next: (res) => {
          if (res.success) {
            this.fetchDocuments(); // Refresh documents after ingestion
          }
        },
        error: (err) => {
          this.errorMessage.set('Failed to fetch Outlook emails.');
          console.error(err);
        },
      });
  }

  // Upload Modal Actions
  openUploadModal() {
    this.isUploadModalOpen.set(true);
    this.selectedFile.set(null);
    this.errorMessage.set(null);
  }

  closeUploadModal() {
    this.isUploadModalOpen.set(false);
    this.selectedFile.set(null);
  }

  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      this.selectedFile.set(input.files[0]);
    }
  }

  uploadDocument() {
    const file = this.selectedFile();
    if (!file) return;

    this.isUploading.set(true);
    this.dashboardService
      .uploadDocument(file)
      .pipe(finalize(() => this.isUploading.set(false)))
      .subscribe({
        next: (res) => {
          if (res.success) {
            this.closeUploadModal();
            this.fetchDocuments(); // Refresh documents
          }
        },
        error: (err) => {
          this.errorMessage.set('Failed to upload document.');
          console.error(err);
        },
      });
  }

  // Document Processing
  processDocument(docId: string) {
    this.processingDocs.update((state) => ({ ...state, [docId]: true }));

    // Optimistically update document status
    this.documents.update((docs) =>
      docs.map((d) => (d.id === docId ? { ...d, processing_status: 'processing' } : d)),
    );

    this.dashboardService
      .processDocument(docId)
      .pipe(
        finalize(() => {
          this.processingDocs.update((state) => {
            const newState = { ...state };
            delete newState[docId];
            return newState;
          });
        }),
      )
      .subscribe({
        next: (res) => {
          if (res.success) {
            this.fetchDocuments();
          }
        },
        error: (err) => {
          this.errorMessage.set('Failed to process document.');
          console.error(err);
          this.fetchDocuments(); // Refresh to get actual state
        },
      });
  }

  viewResult(docId: string) {
    this.isLoadingResult.set(true);
    this.isResultModalOpen.set(true);
    this.errorMessage.set(null);

    this.dashboardService
      .getDocumentResult(docId)
      .pipe(finalize(() => this.isLoadingResult.set(false)))
      .subscribe({
        next: (result) => {
          this.selectedResult.set(result);
        },
        error: (err) => {
          this.errorMessage.set('Failed to load document result.');
          console.error(err);
          this.closeResultModal();
        },
      });
  }

  closeResultModal() {
    this.isResultModalOpen.set(false);
    this.selectedResult.set(null);
  }

  // Auth Actions
  logout() {
    console.log('Outlook clicked');
    this.authService.removeAccessToken();
    this.router.navigate(['/']);
  }
}
