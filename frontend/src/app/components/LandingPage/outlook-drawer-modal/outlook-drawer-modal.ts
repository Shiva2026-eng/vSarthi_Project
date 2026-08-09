import { Component, EventEmitter, Input, Output } from '@angular/core';
import { DatePipe } from '@angular/common';

@Component({
  selector: 'app-outlook-drawer-modal',
  imports: [DatePipe],
  templateUrl: './outlook-drawer-modal.html',
  styleUrl: './outlook-drawer-modal.scss',
})
export class OutlookDrawerModal {
  @Input() showDrawer: boolean = false;
  @Input() outlookMessages: any[] = [];
  @Input() ingestingMessageId: string | null = null;
  @Input() ingestingAllEmails: boolean = false;

  @Output() closeDrawer = new EventEmitter<void>();
  @Output() importEmail = new EventEmitter<any>();
  @Output() importAll = new EventEmitter<void>();

  onClose() {
    this.closeDrawer.emit();
  }

  onImportEmail(msg: any) {
    this.importEmail.emit(msg);
  }

  onImportAll() {
    this.importAll.emit();
  }
}
