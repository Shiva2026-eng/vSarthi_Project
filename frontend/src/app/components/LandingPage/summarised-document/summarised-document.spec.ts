import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SummarisedDocument } from './summarised-document';

describe('SummarisedDocument', () => {
  let component: SummarisedDocument;
  let fixture: ComponentFixture<SummarisedDocument>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SummarisedDocument],
    }).compileComponents();

    fixture = TestBed.createComponent(SummarisedDocument);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
