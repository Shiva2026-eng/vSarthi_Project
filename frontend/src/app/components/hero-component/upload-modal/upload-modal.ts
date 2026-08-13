import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-upload-modal',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './upload-modal.html',
  styleUrl: './upload-modal.scss'
})
export class UploadModal {
  @Input() isOpen = false;
  @Input() selectedFile: File | null = null;
  @Input() isUploading = false;

  @Output() closeModal = new EventEmitter<void>();
  @Output() fileSelected = new EventEmitter<Event>();
  @Output() uploadClicked = new EventEmitter<void>();
}
