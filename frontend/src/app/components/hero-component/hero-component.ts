import { Component } from '@angular/core';
import { SideBar } from '../side-bar/side-bar';

@Component({
  selector: 'app-hero-component',
  imports: [SideBar],
  templateUrl: './hero-component.html',
  styleUrl: './hero-component.scss',
})
export class HeroComponent {}
