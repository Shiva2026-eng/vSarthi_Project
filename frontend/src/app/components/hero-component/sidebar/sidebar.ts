import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { UserProfile } from '../../../services/dashboard.service';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './sidebar.html',
  styleUrl: './sidebar.scss'
})
export class Sidebar {
  @Input() userProfile: UserProfile | null = null;
  @Input() isFetchingEmails = false;
  @Input() isLoadingProfile = false;

  @Output() uploadClicked = new EventEmitter<void>();
  @Output() connectOutlookClicked = new EventEmitter<void>();
  @Output() fetchEmailsClicked = new EventEmitter<void>();
  @Output() logoutClicked = new EventEmitter<void>();
}
