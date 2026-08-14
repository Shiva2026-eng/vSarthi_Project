import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTableModule } from '@angular/material/table';

interface CtaItem {
  id: string;
  documentName: string;
  action: string;
  priority: 'High' | 'Medium' | 'Low';
  date: string;
}

@Component({
  selector: 'app-call-to-action',
  standalone: true,
  imports: [CommonModule, MatTableModule],
  templateUrl: './call-to-action.html',
  styleUrl: './call-to-action.scss',
})
export class CallToAction {
  displayedColumns: string[] = ['documentName', 'action', 'priority', 'date'];
  recentCtas: CtaItem[] = [
    {
      id: '1',
      documentName: 'Q3_Financial_Report.pdf',
      action: 'Review and approve budget allocations for next quarter',
      priority: 'High',
      date: '2026-08-14'
    },
    {
      id: '2',
      documentName: 'Project_Proposal_Alpha.docx',
      action: 'Sign off on project deliverables',
      priority: 'Medium',
      date: '2026-08-13'
    },
    {
      id: '3',
      documentName: 'Vendor_Agreement.pdf',
      action: 'Verify terms and conditions before signing',
      priority: 'High',
      date: '2026-08-12'
    }
  ];
}
