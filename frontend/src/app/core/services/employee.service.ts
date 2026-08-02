import { HttpClient } from '@angular/common/http';

import {
  Injectable,
  inject
} from '@angular/core';

import {
  Observable,
  map
} from 'rxjs';

import { environment } from '../../../environments/environment';

import {
  CreateEmployeeRequest,
  Employee,
  EmployeeRole,
  UpdateEmployeeRequest,
  UpdateUserRoleResponse
} from '../models/employee.model';


@Injectable({
  providedIn: 'root'
})
export class EmployeeService {

  private readonly http = inject(HttpClient);

  private readonly apiRoot =
    environment.apiUrl.replace(/\/+$/, '');

  private readonly employeeApiUrl =
    `${this.apiRoot}/employees`;

  private readonly authApiUrl =
    `${this.apiRoot}/auth`;


  getEmployees(): Observable<Employee[]> {
    return this.http
      .get<Employee[]>(
        this.employeeApiUrl
      )
      .pipe(
        map(employees =>
          employees.map(employee =>
            this.normalizeEmployee(employee)
          )
        )
      );
  }


  getEmployee(
    employeeId: number
  ): Observable<Employee> {
    return this.http
      .get<Employee>(
        `${this.employeeApiUrl}/${employeeId}`
      )
      .pipe(
        map(employee =>
          this.normalizeEmployee(employee)
        )
      );
  }


  getMyProfile(): Observable<Employee> {
    return this.http
      .get<Employee>(
        `${this.employeeApiUrl}/me`
      )
      .pipe(
        map(employee =>
          this.normalizeEmployee(employee)
        )
      );
  }


  createEmployee(
    request: CreateEmployeeRequest
  ): Observable<Employee> {
    return this.http
      .post<Employee>(
        `${this.employeeApiUrl}/create-with-user`,
        request
      )
      .pipe(
        map(employee =>
          this.normalizeEmployee(employee)
        )
      );
  }


  updateEmployee(
    employeeId: number,
    request: UpdateEmployeeRequest
  ): Observable<Employee> {
    return this.http
      .put<Employee>(
        `${this.employeeApiUrl}/${employeeId}`,
        request
      )
      .pipe(
        map(employee =>
          this.normalizeEmployee(employee)
        )
      );
  }


  deleteEmployee(
    employeeId: number
  ): Observable<void> {
    return this.http.delete<void>(
      `${this.employeeApiUrl}/${employeeId}`
    );
  }


  updateUserRole(
  userId: number,
  role: Exclude<
    EmployeeRole,
    'PLATFORM_OWNER'
  >
  ): Observable<UpdateUserRoleResponse> {
    return this.http.put<UpdateUserRoleResponse>(
      `${this.authApiUrl}/users/${userId}/role`,
      {
        role
      }
   );
  }


  disableUser(
    userId: number
  ): Observable<UpdateUserRoleResponse> {
    return this.http.patch<UpdateUserRoleResponse>(
      `${this.authApiUrl}/users/${userId}/disable`,
      {}
    );
  }


  activateUser(
    userId: number
  ): Observable<UpdateUserRoleResponse> {
    return this.http.patch<UpdateUserRoleResponse>(
      `${this.authApiUrl}/users/${userId}/activate`,
      {}
    );
  }


  resetPassword(
    userId: number,
    temporaryPassword: string
  ): Observable<UpdateUserRoleResponse> {
    return this.http.post<UpdateUserRoleResponse>(
      `${this.authApiUrl}/users/${userId}/reset-password`,
      {
        temporary_password:
          temporaryPassword
      }
    );
  }


  private normalizeEmployee(
    employee: Employee
  ): Employee {
    const departmentName =
      employee.team?.department?.name ??
      employee.department ??
      '';

    return {
      ...employee,

      department:
        departmentName,

      username:
        employee.username ??
        employee.user?.username ??
        null,

      role:
        employee.role ??
        employee.user?.role ??
        null,

      is_active:
        employee.is_active ??
        employee.user?.is_active ??
        true,

      must_change_password:
        employee.must_change_password ??
        employee.user?.must_change_password ??
        false,

      full_name:
        employee.full_name ??
        `${employee.first_name} ${employee.last_name}`
          .trim()
    };
  }
}
