import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { ProcessedDocumentResult } from '../../../services/dashboard.service';

@Component({
  selector: 'app-result-modal',
  standalone: true,
  imports: [CommonModule, MatProgressSpinnerModule],
  templateUrl: './result-modal.html',
  styleUrl: './result-modal.scss',
})
export class ResultModal {
  @Input() isOpen = false;
  @Input() selectedResult: ProcessedDocumentResult | null = null;
  @Input() isLoadingResult = false;

  @Output() closeModal = new EventEmitter<void>();
}
