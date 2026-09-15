import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../core/services/auth.service';

interface Announcement {
  id: number;
  title: string;
  category: string;
  date: string;
  author: string;
  content: string;
  isPinned: boolean;
}

@Component({
  selector: 'app-announcements',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './announcements.component.html',
  styleUrl: './announcements.component.scss'
})
export class AnnouncementsComponent {
  private authService = inject(AuthService);

  get isManager(): boolean {
    return this.authService.getStoredUser()?.role === 'YONETICI';
  }

  showModal = false;
  newTitle = '';
  newCategory = 'Genel';
  newContent = '';

  announcements: Announcement[] = [
    {
      id: 1,
      title: 'Cumhuriyet Bayramı ve İdari İzin Duyurusu',
      category: 'Resmi Tatil',
      date: '28 Ekim 2026',
      author: 'İnsan Kaynakları',
      content: '29 Ekim Cumhuriyet Bayramı sebebiyle 28 Ekim saat 13:00 itibarıyla şirketimiz idari tatildedir.',
      isPinned: true
    },
    {
      id: 2,
      title: 'Ofis İçi Hibrit Çalışma ve Yemekhane Menüsü Güncellendi',
      category: 'Ofis Yönetimi',
      date: '15 Eylül 2026',
      author: 'Genel İdare',
      content: 'Yeni ay ile birlikte yemekhane menüleri ve servis kalkış saatleri güncellenmiştir. Detaylar panoya asılmıştır.',
      isPinned: false
    }
  ];

  addAnnouncement(): void {
    if (!this.newTitle || !this.newContent) return;

    this.announcements.unshift({
      id: Date.now(),
      title: this.newTitle,
      category: this.newCategory,
      date: 'Bugün',
      author: this.authService.getStoredUser()?.username || 'Yönetici',
      content: this.newContent,
      isPinned: false
    });

    this.newTitle = '';
    this.newContent = '';
    this.showModal = false;
  }
}
