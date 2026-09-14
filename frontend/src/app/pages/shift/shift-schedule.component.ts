import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { AuthService } from '../../core/services/auth.service';

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

  apiUrl = 'https://hr-management-api-6rpx.onrender.com/operations/shifts';

  get isManager(): boolean {
    return this.authService.getStoredUser()?.role === 'YONETICI';
  }

  todayShift: any = {
    start_time: '09:00',
    end_time: '18:00',
    break_1: '10:30 - 10:45',
    lunch_break: '12:30 - 13:00',
    break_2: '15:00 - 15:15',
    break_3: '16:45 - 17:00'
  };

  showEditModal = false;

  ngOnInit(): void {
    this.loadShift();
  }

  loadShift(): void {
    this.http.get<any>(`${this.apiUrl}/today`).subscribe({
      next: (res) => { if (res) this.todayShift = res; },
      error: (err) => console.error(err)
    });
  }

  saveShift(): void {
    this.http.post(this.apiUrl, this.todayShift).subscribe({
      next: () => {
        alert('Vardiya ve mola saatleri güncellendi!');
        this.showEditModal = false;
        this.loadShift();
      },
      error: (err) => alert('Hata: ' + err.message)
    });
  }
}
