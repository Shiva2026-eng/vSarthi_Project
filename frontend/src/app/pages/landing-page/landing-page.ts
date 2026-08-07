import { Component, inject, OnInit, signal } from '@angular/core';
import { Dashboard } from '../../components/LandingPage/dashboard/dashboard';
import { SectionBanner } from '../../components/LandingPage/section-banner/section-banner';
import { AuthService } from '../../services/auth-service';
import { HttpClient } from '@angular/common/http';
interface Response {
  success: boolean;
  message: Document[];
}
interface Document {
  created_at: string;
  extension: string;
  filename: string;
  id: string;
  mime_type: string;
  size: number;
  source: string;
  user_id: string;
}
@Component({
  selector: 'app-landing-page',
  imports: [Dashboard, SectionBanner],
  templateUrl: './landing-page.html',
  styleUrl: './landing-page.scss',
})
export class LandingPage implements OnInit {
  private http = inject(HttpClient);
  private auth_service = inject(AuthService);
  documents = signal<Document[]>([]);
  ngOnInit(): void {
    this.http
      .get<Response>('http://127.0.0.1:8000/documents/get_all_documents', {
        headers: {
          Authorization: `Bearer ${this.auth_service.getAccessToken()}`,
        },
      })
      .subscribe({
        next: (response) => {
          this.documents.set(response.message);
        },
        error: (e) => {
          console.log(e);
        },
      });
  }
  getSizeInKB(bytes: number): string {
    return (bytes / 1024).toFixed(2);
  }
}
