import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-notification-banner',
  imports: [],
  templateUrl: './notification-banner.html',
  styleUrl: './notification-banner.scss',
})
export class NotificationBanner {
  @Input({ required: true }) message?: string;
  @Input({ required: true }) type!: 'success' | 'error';
}
