import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SectionBannerCard } from './section-banner-card';

describe('SectionBannerCard', () => {
  let component: SectionBannerCard;
  let fixture: ComponentFixture<SectionBannerCard>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SectionBannerCard],
    }).compileComponents();

    fixture = TestBed.createComponent(SectionBannerCard);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
