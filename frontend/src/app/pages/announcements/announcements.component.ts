import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
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
export class AnnouncementsComponent implements OnInit {
  private http = inject(HttpClient);
  private authService = inject(AuthService);

  readonly apiUrl = 'https://hr-management-api-6rpx.onrender.com/announcements';

  get isManager(): boolean {
    const role = this.authService.getStoredUser()?.role;
    return role === 'YONETICI' || role === 'PLATFORM_OWNER';
  }

  showModal = false;
  newTitle = '';
  newCategory = 'Genel';
  newContent = '';
  newIsPinned = false;

  announcements: Announcement[] = [];

  ngOnInit(): void {
    this.loadAnnouncements();
  }

  loadAnnouncements(): void {
    this.http.get<Announcement[]>(this.apiUrl).subscribe({
      next: (data) => {
        this.announcements = data || [];
      },
      error: (err) => console.error('Duyurular getirilemedi:', err)
    });
  }

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
    this.http.put<{ status: string; isPinned: boolean }>(`${this.apiUrl}/${item.id}/toggle-pin`, {}).subscribe({
      next: (res) => {
        item.isPinned = res.isPinned;
        this.loadAnnouncements();
      },
      error: (err) => alert('Sabitleme hatası: ' + (err.error?.detail || err.message))
    });
  }

  addAnnouncement(): void {
    if (!this.newTitle.trim() || !this.newContent.trim()) return;

    const payload = {
      title: this.newTitle.trim(),
      category: this.newCategory,
      content: this.newContent.trim(),
      is_pinned: this.newIsPinned
    };

    this.http.post(this.apiUrl, payload).subscribe({
      next: () => {
        this.newTitle = '';
        this.newContent = '';
        this.newCategory = 'Genel';
        this.newIsPinned = false;
        this.showModal = false;
        this.loadAnnouncements(); // Veritabanından taze veriyi çek
      },
      error: (err) => alert('Duyuru kaydedilemedi: ' + (err.error?.detail || err.message))
    });
  }
}
