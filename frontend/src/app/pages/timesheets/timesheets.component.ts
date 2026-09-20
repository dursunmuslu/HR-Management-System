import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { finalize } from 'rxjs';
import { AuthService } from '../../core/services/auth.service';

type ViewTab = 'TIMESHEETS' | 'SURVEYS';

@Component({
  selector: 'app-timesheets',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './timesheets.component.html',
  styleUrl: './timesheets.component.scss'
})
export class TimesheetsComponent implements OnInit {
  private http = inject(HttpClient);
  private authService = inject(AuthService);

  readonly baseUrl = 'https://hr-management-api-6rpx.onrender.com/timesheets';

  activeTab: ViewTab = 'TIMESHEETS';
  timesheets: any[] = [];
  surveys: any[] = [];

  isLoading = true;
  isUploading = false;
  statusMessage = '';

  get isManagerOrTL(): boolean {
    const role = this.authService.getStoredUser()?.role;
    return role === 'YONETICI' || role === 'PLATFORM_OWNER' || role === 'TAKIM_LIDERI';
  }

  // Login Süreleri İstatistikleri
  get totalMissingMinutes(): number {
    return this.timesheets
      .filter(t => t.diff_minutes < 0)
      .reduce((acc, curr) => acc + Math.abs(curr.diff_minutes), 0);
  }

  get totalOvertimeMinutes(): number {
    return this.timesheets
      .filter(t => t.diff_minutes > 0)
      .reduce((acc, curr) => acc + curr.diff_minutes, 0);
  }

  // Anket İstatistikleri (Personelin ortalama skoru vs hedef)
  get averageSurveyScore(): number {
    if (this.surveys.length === 0) return 0;
    const total = this.surveys.reduce((acc, s) => acc + (s.actual_score || 0), 0);
    return +(total / this.surveys.length).toFixed(1);
  }

  get averageTargetScore(): number {
    if (this.surveys.length === 0) return 0;
    const total = this.surveys.reduce((acc, s) => acc + (s.target_score || 0), 0);
    return +(total / this.surveys.length).toFixed(1);
  }

  ngOnInit(): void {
    this.loadData();
  }

  setTab(tab: ViewTab): void {
    this.activeTab = tab;
  }

  loadData(): void {
    this.isLoading = true;
    const endpoint = this.isManagerOrTL ? '/company-records' : '/my-records';

    this.http.get<any>(`${this.baseUrl}${endpoint}`)
      .pipe(finalize(() => { this.isLoading = false; }))
      .subscribe({
        next: (res) => {
          this.timesheets = res?.timesheets || [];
          this.surveys = res?.surveys || [];
        },
        error: () => {
          this.timesheets = [];
          this.surveys = [];
        }
      });
  }

  onExcelSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (!input.files || input.files.length === 0) return;

    const file = input.files[0];
    const formData = new FormData();
    formData.append('file', file);

    this.isUploading = true;
    this.statusMessage = '';

    this.http.post<any>(`${this.baseUrl}/upload`, formData)
      .pipe(finalize(() => {
        this.isUploading = false;
        input.value = '';
      }))
      .subscribe({
        next: (res) => {
          this.statusMessage = res.message || 'Veriler başarıyla işlendi.';
          this.loadData();
        },
        error: (err) => {
          this.statusMessage = 'Hata: ' + (err.error?.detail || err.message);
        }
      });
  }

  formatMinutes(min: number): string {
    const absMin = Math.abs(min);
    const h = Math.floor(absMin / 60);
    const m = absMin % 60;
    return `${h > 0 ? h + ' saat ' : ''}${m} dk`;
  }
}
