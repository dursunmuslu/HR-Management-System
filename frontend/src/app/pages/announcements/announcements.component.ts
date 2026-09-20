import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../core/services/auth.service';

export interface Announcement {
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
    const role = this.authService.getStoredUser()?.role;
    return role === 'YONETICI' || role === 'PLATFORM_OWNER';
  }

  showModal = false;
  newTitle = '';
  newCategory = 'Genel';
  newContent = '';
  newIsPinned = false;

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

  // Sabitlenenler her zaman en üstte sıralanır
  get sortedAnnouncements(): Announcement[] {
    return [...this.announcements].sort((a, b) => {
      if (a.isPinned === b.isPinned) {
        return b.id - a.id;
      }
      return a.isPinned ? -1 : 1;
    });
  }

  togglePin(item: Announcement): void {
    if (!this.isManager) return;
    item.isPinned = !item.isPinned;
  }

  addAnnouncement(): void {
    if (!this.newTitle.trim() || !this.newContent.trim()) return;

    const currentUser = this.authService.getStoredUser();
    const newEntry: Announcement = {
      id: Date.now(),
      title: this.newTitle.trim(),
      category: this.newCategory,
      date: 'Bugün',
      author: currentUser?.username || 'Yönetici',
      content: this.newContent.trim(),
      isPinned: this.newIsPinned
    };

    this.announcements.unshift(newEntry);

    // Formu temizle ve kapat
    this.newTitle = '';
    this.newContent = '';
    this.newCategory = 'Genel';
    this.newIsPinned = false;
    this.showModal = false;
  }
}
