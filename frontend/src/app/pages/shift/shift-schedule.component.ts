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
  employeesUrl = 'https://hr-management-api-6rpx.onrender.com/employees';

  get isManager(): boolean {
    const role = this.authService.getStoredUser()?.role;
    return role === 'YONETICI' || role === 'PLATFORM_OWNER';
  }

  todayShift: any = {
    start_time: '09:00',
    end_time: '18:00',
    break_1: '10:30 - 10:45',
    lunch_break: '12:30 - 13:00',
    break_2: '15:00 - 15:15',
    break_3: '16:45 - 17:00'
  };

  editForm: any = {};
  selectedEmployeeId: number | null = null;
  employeeList: any[] = [];
  showEditModal = false;

  ngOnInit(): void {
    this.loadShift();
    if (this.isManager) {
      this.loadEmployees();
    }
  }

  loadShift(): void {
    this.http.get<any>(`${this.apiUrl}/today`).subscribe({
      next: (res) => {
        if (res) this.todayShift = res;
      },
      error: (err) => console.error(err)
    });
  }

  loadEmployees(): void {
    this.http.get<any[]>(this.employeesUrl).subscribe({
      next: (res) => {
        this.employeeList = res;
      },
      error: (err) => console.error(err)
    });
  }

  openEditModal(): void {
    this.editForm = { ...this.todayShift };
    this.selectedEmployeeId = null;
    this.showEditModal = true;
  }

  saveShift(): void {
    const payload = {
      ...this.editForm,
      employee_id: this.selectedEmployeeId
    };

    this.http.post(this.apiUrl, payload).subscribe({
      next: () => {
        alert('Vardiya ve mola saatleri başarıyla güncellendi!');
        this.showEditModal = false;
        this.loadShift();
      },
      error: (err) => alert('Hata: ' + (err.error?.detail || err.message))
    });
  }
}
