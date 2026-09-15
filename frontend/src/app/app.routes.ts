import { inject } from '@angular/core';
import { Router, Routes } from '@angular/router';

import { authGuard } from './core/guards/auth.guard';
import { companyUserGuard } from './core/guards/company-user.guard';
import { defaultRouteGuard } from './core/guards/default-route.guard';
import { managerGuard } from './core/guards/manager.guard';
import { platformOwnerGuard } from './core/guards/platform-owner.guard';

import { MainLayoutComponent } from './layout/main-layout/main-layout.component';
import { ChangePasswordComponent } from './pages/change-password/change-password.component';
import { DashboardComponent } from './pages/dashboard/dashboard.component';
import { EmployeeFormComponent } from './pages/employees/employee-form/employee-form.component';
import { EmployeeListComponent } from './pages/employees/employee-list/employee-list.component';
import { CreateLeaveComponent } from './pages/leaves/create-leave/create-leave.component';
import { LeaveRequestsComponent } from './pages/leaves/leave-requests/leave-requests.component';
import { MyLeavesComponent } from './pages/leaves/my-leaves/my-leaves.component';
import { LoginComponent } from './pages/login/login.component';
import { OrganizationManagementComponent } from './pages/organization/organization-management/organization-management.component';
import { PlatformDashboardComponent } from './pages/platform/platform-dashboard/platform-dashboard.component';

import { QuizListComponent } from './pages/quiz/quiz-list.component';
import { ShiftScheduleComponent } from './pages/shift/shift-schedule.component';
import { AnnouncementsComponent } from './pages/announcements/announcements.component';
import { CompanySettingsComponent } from './pages/company-settings/company-settings.component';

// Modül kapalıysa Dashboard'a yönlendiren fonksiyonel Guard'lar
const quizFeatureGuard = () => {
  const router = inject(Router);
  const isEnabled = localStorage.getItem('cfg_show_quizzes') !== 'false';
  return isEnabled ? true : router.createUrlTree(['/dashboard']);
};

const shiftFeatureGuard = () => {
  const router = inject(Router);
  const isEnabled = localStorage.getItem('cfg_show_shifts') !== 'false';
  return isEnabled ? true : router.createUrlTree(['/dashboard']);
};

const announcementFeatureGuard = () => {
  const router = inject(Router);
  const isEnabled = localStorage.getItem('cfg_show_announcements') !== 'false';
  return isEnabled ? true : router.createUrlTree(['/dashboard']);
};

export const routes: Routes = [
  {
    path: 'login',
    component: LoginComponent
  },
  {
    path: 'change-password',
    component: ChangePasswordComponent,
    canActivate: [authGuard]
  },
  {
    path: '',
    component: MainLayoutComponent,
    canActivate: [authGuard],
    children: [
      {
        path: 'platform',
        component: PlatformDashboardComponent,
        canActivate: [platformOwnerGuard]
      },
      {
        path: 'dashboard',
        component: DashboardComponent,
        canActivate: [companyUserGuard]
      },

      // Operasyon, Duyuru & Çalışma Modülleri (Ayarlarla Korunan Rotalar)
      {
        path: 'announcements',
        component: AnnouncementsComponent,
        canActivate: [companyUserGuard, announcementFeatureGuard]
      },
      {
        path: 'quizzes',
        component: QuizListComponent,
        canActivate: [companyUserGuard, quizFeatureGuard]
      },
      {
        path: 'shifts',
        component: ShiftScheduleComponent,
        canActivate: [companyUserGuard, shiftFeatureGuard]
      },

      // İzin İşlemleri
      {
        path: 'leaves/my',
        component: MyLeavesComponent,
        canActivate: [companyUserGuard]
      },
      {
        path: 'leaves/create',
        component: CreateLeaveComponent,
        canActivate: [companyUserGuard]
      },
      {
        path: 'leave-requests',
        component: LeaveRequestsComponent,
        canActivate: [managerGuard]
      },

      // Yönetici İşlemleri
      {
        path: 'organization',
        component: OrganizationManagementComponent,
        canActivate: [managerGuard]
      },
      {
        path: 'employees',
        component: EmployeeListComponent,
        canActivate: [managerGuard]
      },
      {
        path: 'employees/create',
        component: EmployeeFormComponent,
        canActivate: [managerGuard]
      },
      {
        path: 'company-settings',
        component: CompanySettingsComponent,
        canActivate: [managerGuard]
      },

      {
        path: '',
        pathMatch: 'full',
        component: DashboardComponent,
        canActivate: [defaultRouteGuard]
      }
    ]
  },
  {
    path: '**',
    component: DashboardComponent,
    canActivate: [defaultRouteGuard]
  }
];
