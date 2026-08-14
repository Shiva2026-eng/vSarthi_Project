import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CallToAction } from './call-to-action';

describe('CallToAction', () => {
  let component: CallToAction;
  let fixture: ComponentFixture<CallToAction>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CallToAction],
    }).compileComponents();

    fixture = TestBed.createComponent(CallToAction);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
