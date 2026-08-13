import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-dashboard-stats',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard-stats.html',
  styleUrl: './dashboard-stats.scss'
})
export class DashboardStats {
  @Input() totalDocuments = 0;
  @Input() processingDocuments = 0;
  @Input() completedDocuments = 0;
  @Input() isOutlookConnected = false;
}
