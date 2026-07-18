import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, map } from 'rxjs';

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
    'http://localhost:8000';

  private readonly employeeApiUrl =
    `${this.apiRoot}/employees`;

  private readonly authApiUrl =
    `${this.apiRoot}/auth`;

  getEmployees(): Observable<Employee[]> {
    return this.http
      .get<Employee[]>(this.employeeApiUrl)
      .pipe(
        map(employees =>
          employees.map(employee =>
            this.normalizeEmployee(employee)
          )
        )
      );
  }

  getEmployee(id: number): Observable<Employee> {
    return this.http
      .get<Employee>(
        `${this.employeeApiUrl}/${id}`
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
    id: number,
    request: UpdateEmployeeRequest
  ): Observable<Employee> {
    return this.http
      .put<Employee>(
        `${this.employeeApiUrl}/${id}`,
        request
      )
      .pipe(
        map(employee =>
          this.normalizeEmployee(employee)
        )
      );
  }

  deleteEmployee(
    id: number
  ): Observable<void> {
    return this.http.delete<void>(
      `${this.employeeApiUrl}/${id}`
    );
  }

  updateUserRole(
    userId: number,
    role: EmployeeRole
  ): Observable<UpdateUserRoleResponse> {
    return this.http.put<UpdateUserRoleResponse>(
      `${this.authApiUrl}/users/${userId}/role`,
      {
        role
      }
    );
  }

  private normalizeEmployee(
    employee: Employee
  ): Employee {
    return {
      ...employee,

      username:
        employee.username ??
        employee.user?.username ??
        null,

      role:
        employee.role ??
        employee.user?.role ??
        null
    };
  }
}
