import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import {
  RouterLink,
  RouterLinkActive,
  RouterOutlet
} from '@angular/router';

import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-main-layout',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink,
    RouterLinkActive,
    RouterOutlet
  ],
  templateUrl: './main-layout.component.html',
  styleUrl: './main-layout.component.scss'
})
export class MainLayoutComponent {

  private readonly authService = inject(AuthService);

  sidebarOpen = false;

  readonly currentUser = this.authService.getStoredUser();

  get isManager(): boolean {
    return this.currentUser?.role === 'YONETICI';
  }

  get displayName(): string {
    return this.currentUser?.username || 'Kullanıcı';
  }

  get roleLabel(): string {
    return this.isManager ? 'Yönetici' : 'Personel';
  }

  get userInitial(): string {
    return this.displayName
      .charAt(0)
      .toLocaleUpperCase('tr-TR');
  }

  toggleSidebar(): void {
    this.sidebarOpen = !this.sidebarOpen;
  }

  closeSidebar(): void {
    this.sidebarOpen = false;
  }

  logout(): void {
    this.authService.logout();
  }
}
