import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SectionBanner } from './section-banner';

describe('SectionBanner', () => {
  let component: SectionBanner;
  let fixture: ComponentFixture<SectionBanner>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SectionBanner],
    }).compileComponents();

    fixture = TestBed.createComponent(SectionBanner);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
