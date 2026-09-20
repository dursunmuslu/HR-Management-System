import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { finalize } from 'rxjs';

export interface CompanyModuleSettings {
  is_announcements_enabled: boolean;
  is_quizzes_enabled: boolean;
  is_shifts_enabled: boolean;
  is_leaves_enabled: boolean;
  is_timesheets_enabled: boolean;
}

@Component({
  selector: 'app-company-settings',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './company-settings.component.html',
  styleUrl: './company-settings.component.scss'
})
export class CompanySettingsComponent implements OnInit {
  private http = inject(HttpClient);

  readonly apiUrl = 'https://hr-management-api-6rpx.onrender.com/companies/my-settings';

  settings: CompanyModuleSettings = {
    is_announcements_enabled: true,
    is_quizzes_enabled: true,
    is_shifts_enabled: true,
    is_leaves_enabled: true,
    is_timesheets_enabled: true
  };

  isSaving = false;
  statusMessage = '';
  isSuccess = false;

  ngOnInit(): void {
    this.loadSettings();
  }

  loadSettings(): void {
    this.http.get<CompanyModuleSettings>(this.apiUrl).subscribe({
      next: (res) => {
        if (res) {
          this.settings = { ...this.settings, ...res };
          this.syncLocalStorage();
        }
      },
      error: () => {
        // Varsayılan olarak açık kalır
      }
    });
  }

  saveSettings(): void {
    this.isSaving = true;
    this.statusMessage = '';

    this.http.put<CompanyModuleSettings>(this.apiUrl, this.settings)
      .pipe(finalize(() => { this.isSaving = false; }))
      .subscribe({
        next: (res) => {
          if (res) {
            this.settings = { ...this.settings, ...res };
          }
          this.syncLocalStorage();
          this.isSuccess = true;
          this.statusMessage = 'Şirket modül ayarları başarıyla kaydedildi.';
        },
        error: (err) => {
          this.isSuccess = false;
          this.statusMessage = 'Ayar kaydedilirken bir hata oluştu: ' + (err.error?.detail || err.message);
        }
      });
  }

  private syncLocalStorage(): void {
    localStorage.setItem('cfg_show_quizzes', String(this.settings.is_quizzes_enabled));
    localStorage.setItem('cfg_show_shifts', String(this.settings.is_shifts_enabled));
    localStorage.setItem('cfg_show_announcements', String(this.settings.is_announcements_enabled));
    localStorage.setItem('cfg_show_timesheets', String(this.settings.is_timesheets_enabled));
  }
}
