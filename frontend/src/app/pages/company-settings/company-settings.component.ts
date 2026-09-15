import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-company-settings',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './company-settings.component.html',
  styleUrl: './company-settings.component.scss'
})
export class CompanySettingsComponent {
  cfgQuizzes = localStorage.getItem('cfg_show_quizzes') !== 'false';
  cfgShifts = localStorage.getItem('cfg_show_shifts') !== 'false';
  cfgAnnouncements = localStorage.getItem('cfg_show_announcements') !== 'false';

  saveConfig(): void {
    localStorage.setItem('cfg_show_quizzes', this.cfgQuizzes.toString());
    localStorage.setItem('cfg_show_shifts', this.cfgShifts.toString());
    localStorage.setItem('cfg_show_announcements', this.cfgAnnouncements.toString());
  }
}
