import { ComponentFixture, TestBed } from '@angular/core/testing';

import { NotificationBanner } from './notification-banner';

describe('NotificationBanner', () => {
  let component: NotificationBanner;
  let fixture: ComponentFixture<NotificationBanner>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [NotificationBanner],
    }).compileComponents();

    fixture = TestBed.createComponent(NotificationBanner);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
