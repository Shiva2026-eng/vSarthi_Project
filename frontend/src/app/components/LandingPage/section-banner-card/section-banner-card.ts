import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-section-banner-card',
  imports: [],
  templateUrl: './section-banner-card.html',
  styleUrl: './section-banner-card.scss',
})
export class SectionBannerCard {
  @Input() imageURL?: string;
  @Input() name?: string;
}
