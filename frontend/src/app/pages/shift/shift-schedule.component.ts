import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { AuthService } from '../../core/services/auth.service';

export type ShiftViewMode = 'DAILY' | 'WEEKLY';

export interface ShiftItem {
  employee_id: number | null;
  tc_no?: string;
  full_name?: string;
  team_name?: string;
  job_title?: string;
  shift_date: string;
  start_time: string;
  end_time: string;
  break_1: string;
  lunch_break: string;
  break_2: string;
  break_3: string;
}

@Component({
  selector: 'app-shift-schedule',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './shift-schedule.component.html',
  styleUrl: './shift-schedule.component.scss'
})
export class ShiftScheduleComponent implements OnInit {
  private http = inject(HttpClient);
  private authService = inject(AuthService);

  readonly apiUrl = 'https://hr-management-api-6rpx.onrender.com/operations/shifts';
  readonly employeesUrl = 'https://hr-management-api-6rpx.onrender.com/employees';
  readonly bulkShiftUrl = 'https://hr-management-api-6rpx.onrender.com/bulk/upload-shifts';

  viewMode: ShiftViewMode = 'DAILY';
  selectedDate: string = new Date().toISOString().substring(0, 10);

  get isManager(): boolean {
    const role = this.authService.getStoredUser()?.role;
    return role === 'YONETICI' || role === 'PLATFORM_OWNER';
  }

  get isLeaderOrManager(): boolean {
    const role = this.authService.getStoredUser()?.role;
    return role === 'YONETICI' || role === 'PLATFORM_OWNER' || role === 'TAKIM_LIDERI';
  }

  todayShift: ShiftItem = {
    employee_id: null,
    shift_date: this.selectedDate,
    start_time: '09:00',
    end_time: '18:00',
    break_1: '10:30 - 10:45',
    lunch_break: '12:30 - 13:00',
    break_2: '15:00 - 15:15',
    break_3: '16:45 - 17:00'
  };

  dailyList: ShiftItem[] = [];
  employeeList: any[] = [];
  editForm: Partial<ShiftItem> = {};
  selectedEmployeeId: number | null = null;
  showEditModal = false;

  selectedFile: File | null = null;
  uploadStatusMessage = '';

  ngOnInit(): void {
    this.loadMyTodayShift();
    if (this.isLeaderOrManager) {
      this.loadDailyList();
      this.loadEmployees();
    }
  }

  switchMode(mode: ShiftViewMode): void {
    this.viewMode = mode;
    if (mode === 'DAILY' && this.isLeaderOrManager) {
      this.loadDailyList();
    }
  }

  loadMyTodayShift(): void {
    this.http.get<ShiftItem>(`${this.apiUrl}/today`).subscribe({
      next: (res) => {
        if (res) this.todayShift = res;
      },
      error: (err) => console.error('Kişisel vardiya yüklenemedi:', err)
    });
  }

  loadDailyList(): void {
    this.http.get<ShiftItem[]>(`${this.apiUrl}/daily-list?shift_date=${this.selectedDate}`).subscribe({
      next: (res) => {
        this.dailyList = res || [];
      },
      error: (err) => console.error('Günlük liste yüklenemedi:', err)
    });
  }

  loadEmployees(): void {
    this.http.get<any[]>(this.employeesUrl).subscribe({
      next: (res) => {
        this.employeeList = res || [];
      },
      error: (err) => console.error('Personel listesi yüklenemedi:', err)
    });
  }

  openGeneralEditModal(): void {
    this.editForm = { ...this.todayShift, shift_date: this.selectedDate };
    this.selectedEmployeeId = null;
    this.showEditModal = true;
  }

  openSingleEditModal(item: ShiftItem): void {
    this.editForm = { ...item, shift_date: this.selectedDate };
    this.selectedEmployeeId = item.employee_id;
    this.showEditModal = true;
  }

  saveShift(): void {
    const payload = {
      ...this.editForm,
      shift_date: this.selectedDate,
      employee_id: this.selectedEmployeeId
    };

    this.http.post(this.apiUrl, payload).subscribe({
      next: () => {
        alert('Vardiya ve mola saatleri başarıyla kaydedildi!');
        this.showEditModal = false;
        this.loadMyTodayShift();
        if (this.isLeaderOrManager) {
          this.loadDailyList();
        }
      },
      error: (err) => alert('Kayıt Hatası: ' + (err.error?.detail || err.message))
    });
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      this.selectedFile = input.files[0];
    }
  }

  uploadExcel(): void {
    if (!this.selectedFile) return;

    const formData = new FormData();
    formData.append('file', this.selectedFile);

    this.http.post<any>(this.bulkShiftUrl, formData).subscribe({
      next: (res) => {
        this.uploadStatusMessage = res.message || 'Excel başarıyla işlendi!';
        this.selectedFile = null;
        this.loadDailyList();
        this.loadMyTodayShift();
      },
      error: (err) => alert('Excel aktarım hatası: ' + (err.error?.detail || err.message))
    });
  }
}
