import { Routes } from '@angular/router';

import { authGuard } from './core/guards/auth.guard';
import { managerGuard } from './core/guards/manager.guard';

import {
  MainLayoutComponent
} from './layout/main-layout/main-layout.component';

import {
  LoginComponent
} from './pages/login/login.component';

import {
  DashboardComponent
} from './pages/dashboard/dashboard.component';

import {
  MyLeavesComponent
} from './pages/leaves/my-leaves/my-leaves.component';

import {
  CreateLeaveComponent
} from './pages/leaves/create-leave/create-leave.component';

import {
  LeaveRequestsComponent
} from './pages/leaves/leave-requests/leave-requests.component';

import {
  EmployeeListComponent
} from './pages/employees/employee-list/employee-list.component';

import {
  EmployeeFormComponent
} from './pages/employees/employee-form/employee-form.component';

export const routes: Routes = [
  {
    path: 'login',
    component: LoginComponent
  },
  {
    path: '',
    component: MainLayoutComponent,
    canActivate: [
      authGuard
    ],
    children: [
      {
        path: 'dashboard',
        component: DashboardComponent
      },
      {
        path: 'leaves/my',
        component: MyLeavesComponent
      },
      {
        path: 'leaves/create',
        component: CreateLeaveComponent
      },
      {
        path: 'leave-requests',
        component: LeaveRequestsComponent,
        canActivate: [
          managerGuard
        ]
      },
      {
        path: 'employees',
        component: EmployeeListComponent,
        canActivate: [
          managerGuard
        ]
      },
      {
        path: 'employees/create',
        component: EmployeeFormComponent,
        canActivate: [
          managerGuard
        ]
      },
      {
        path: '',
        pathMatch: 'full',
        redirectTo: 'dashboard'
      }
    ]
  },
  {
    path: '**',
    redirectTo: 'dashboard'
  }
];
