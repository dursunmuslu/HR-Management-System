import { Routes } from '@angular/router';

import {
  authGuard
} from './core/guards/auth.guard';

import {
  companyUserGuard
} from './core/guards/company-user.guard';

import {
  defaultRouteGuard
} from './core/guards/default-route.guard';

import {
  managerGuard
} from './core/guards/manager.guard';

import {
  platformOwnerGuard
} from './core/guards/platform-owner.guard';

import {
  MainLayoutComponent
} from './layout/main-layout/main-layout.component';

import {
  ChangePasswordComponent
} from './pages/change-password/change-password.component';

import {
  DashboardComponent
} from './pages/dashboard/dashboard.component';

import {
  EmployeeFormComponent
} from './pages/employees/employee-form/employee-form.component';

import {
  EmployeeListComponent
} from './pages/employees/employee-list/employee-list.component';

import {
  CreateLeaveComponent
} from './pages/leaves/create-leave/create-leave.component';

import {
  LeaveRequestsComponent
} from './pages/leaves/leave-requests/leave-requests.component';

import {
  MyLeavesComponent
} from './pages/leaves/my-leaves/my-leaves.component';

import {
  LoginComponent
} from './pages/login/login.component';

import {
  OrganizationManagementComponent
} from './pages/organization/organization-management/organization-management.component';

import {
  PlatformDashboardComponent
} from './pages/platform/platform-dashboard/platform-dashboard.component';


export const routes: Routes = [
  {
    path: 'login',
    component: LoginComponent
  },

  {
    path: 'change-password',
    component: ChangePasswordComponent,
    canActivate: [
      authGuard
    ]
  },

  {
    path: '',
    component: MainLayoutComponent,

    canActivate: [
      authGuard
    ],

    children: [
      {
        path: 'platform',
        component: PlatformDashboardComponent,

        canActivate: [
          platformOwnerGuard
        ]
      },

      {
        path: 'dashboard',
        component: DashboardComponent,

        canActivate: [
          companyUserGuard
        ]
      },

      {
        path: 'leaves/my',
        component: MyLeavesComponent,

        canActivate: [
          companyUserGuard
        ]
      },

      {
        path: 'leaves/create',
        component: CreateLeaveComponent,

        canActivate: [
          companyUserGuard
        ]
      },

      {
        path: 'leave-requests',
        component: LeaveRequestsComponent,

        canActivate: [
          managerGuard
        ]
      },

      {
        path: 'organization',
        component:
          OrganizationManagementComponent,

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

        component: DashboardComponent,

        canActivate: [
          defaultRouteGuard
        ]
      }
    ]
  },

  {
    path: '**',

    component: DashboardComponent,

    canActivate: [
      defaultRouteGuard
    ]
  }
];
