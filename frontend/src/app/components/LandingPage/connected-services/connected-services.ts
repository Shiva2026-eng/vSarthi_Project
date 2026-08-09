import { Component, EventEmitter, Input, Output, signal } from '@angular/core';
import { ConnectedAccounts } from '../../../services/auth-service';

@Component({
  selector: 'app-connected-services',
  imports: [],
  templateUrl: './connected-services.html',
  styleUrl: './connected-services.scss',
})
export class ConnectedServices {
  @Input() connectedAccounts = signal<ConnectedAccounts>({ outlook: false, telegram: false });
  @Input() loadingOutlookMessages = signal<boolean>(false);

  @Output() connectOutlook = new EventEmitter<void>();
  @Output() fetchOutlookEmails = new EventEmitter<void>();

  onConnectOutlook() {
    this.connectOutlook.emit();
  }

  onFetchOutlookEmails() {
    this.fetchOutlookEmails.emit();
  }
}
