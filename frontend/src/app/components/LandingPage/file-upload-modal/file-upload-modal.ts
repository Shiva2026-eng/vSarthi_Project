import { Component, EventEmitter, inject, Input, Output } from '@angular/core';
import { DocumentsService } from '../../../services/documents-service';

@Component({
  selector: 'app-file-upload-modal',
  imports: [],
  templateUrl: './file-upload-modal.html',
  styleUrl: './file-upload-modal.scss',
})
export class FileUploadModal {
  @Input() showModal: boolean = false;
  @Output() toggleModal = new EventEmitter<void>();
  @Output() fileUploaded = new EventEmitter<void>();

  selectedFile: File | null = null;
  isUploading: boolean = false;
  private documentService = inject(DocumentsService);

  onCloseModal() {
    this.selectedFile = null;
    this.toggleModal.emit();
  }

  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      this.selectedFile = input.files[0];
      console.log(this.selectedFile);
    }
  }

  uploadFile() {
    if (!this.selectedFile) {
      alert('Select a file first');
      return;
    }

    this.isUploading = true;
    this.documentService.uploadDocument(this.selectedFile).subscribe({
      next: (response) => {
        console.log('Upload success:', response);
        this.selectedFile = null;
        this.isUploading = false;
        this.fileUploaded.emit();
        this.toggleModal.emit();
      },
      error: (e) => {
        console.error('Upload error:', e);
        this.isUploading = false;
        alert('Failed to upload file. Please try again.');
      },
    });
  }
}

