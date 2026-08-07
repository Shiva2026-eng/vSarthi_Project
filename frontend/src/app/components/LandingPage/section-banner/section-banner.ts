import { Component } from '@angular/core';
import { SectionBannerCard } from '../section-banner-card/section-banner-card';
const accounts = [
  {
    name: 'OutLook',
    imageURL:
      'https://static.vecteezy.com/system/resources/previews/060/587/623/non_2x/rectangle-microsoft-outlook-new-icon-logo-symbol-free-png.png',
  },
  {
    name: 'WhatsApp',
    imageURL:
      'https://png.pngtree.com/png-clipart/20230426/original/pngtree-whatsapp-social-media-icon-design-template-vector-whatsapp-logo-picture-image_3654780.png',
  },
  {
    name: 'GMail',
    imageURL:
      'https://static.vecteezy.com/system/resources/previews/021/514/743/non_2x/google-gmail-logo-symbol-design-illustration-free-vector.jpg',
  },
  {
    name: 'Telegram',
    imageURL:
      'https://static.vecteezy.com/system/resources/previews/023/986/562/non_2x/telegram-logo-telegram-logo-transparent-telegram-icon-transparent-free-free-png.png',
  },
];
@Component({
  selector: 'app-section-banner',
  imports: [SectionBannerCard],
  templateUrl: './section-banner.html',
  styleUrl: './section-banner.scss',
})
export class SectionBanner {
  accounts = accounts;
}
