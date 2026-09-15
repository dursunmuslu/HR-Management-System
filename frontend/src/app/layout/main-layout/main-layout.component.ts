import { CommonModule } from '@angular/common';

import {
  Component,
  inject
} from '@angular/core';

import {
  RouterLink,
  RouterLinkActive,
  RouterOutlet
} from '@angular/router';

import {
  AuthService
} from '../../core/services/auth.service';


@Component({
  selector: 'app-main-layout',

  standalone: true,

  imports: [
    CommonModule,
    RouterLink,
    RouterLinkActive,
    RouterOutlet
  ],

  templateUrl:
    './main-layout.component.html',

  styleUrl:
    './main-layout.component.scss'
})
export class MainLayoutComponent {

  private readonly authService =
    inject(AuthService);

  sidebarOpen = false;

  get currentUser() {
    return this.authService
      .getStoredUser();
  }

  get isPlatformOwner(): boolean {
    return (
      this.currentUser?.role ===
      'PLATFORM_OWNER'
    );
  }
    // main-layout.component.ts içinde bir yere ekle:
  get showQuizzes(): boolean {
    return localStorage.getItem('cfg_show_quizzes') !== 'false';
  }

  get showShifts(): boolean {
    return localStorage.getItem('cfg_show_shifts') !== 'false';
  }

  get showAnnouncements(): boolean {
    return localStorage.getItem('cfg_show_announcements') !== 'false';
  }


  get isManager(): boolean {
    return (
      this.currentUser?.role ===
      'YONETICI'
    );
  }

  get isEmployee(): boolean {
    return (
      this.currentUser?.role ===
      'PERSONEL'
    );
  }

  get homeRoute(): string {
    return this.isPlatformOwner
      ? '/platform'
      : '/dashboard';
  }

  get displayName(): string {
    return (
      this.currentUser?.username ||
      'Kullanıcı'
    );
  }

  get roleLabel(): string {
    if (this.isPlatformOwner) {
      return 'Sistem Sahibi';
    }

    if (this.isManager) {
      return 'Şirket Yöneticisi';
    }

    if (this.isEmployee) {
      return 'Personel';
    }

    return 'Kullanıcı';
  }

  get applicationTitle(): string {
    return this.isPlatformOwner
      ? 'HR Platform Yönetimi'
      : 'İnsan Kaynakları Yönetim Sistemi';
  }

  get applicationDescription(): string {
    return this.isPlatformOwner
      ? 'Şirketleri ve platform erişimlerini yönetin'
      : 'Personel ve izin süreçlerinizi yönetin';
  }

  get userInitial(): string {
    return this.displayName
      .charAt(0)
      .toLocaleUpperCase(
        'tr-TR'
      );
  }

  toggleSidebar(): void {
    this.sidebarOpen =
      !this.sidebarOpen;
  }

  closeSidebar(): void {
    this.sidebarOpen = false;
  }

  logout(): void {
    this.authService.logout();
  }
}
