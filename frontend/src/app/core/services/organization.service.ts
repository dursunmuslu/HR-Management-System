import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';

import {
  Company,
  CreateCompanyRequest,
  CreateDepartmentRequest,
  CreateTeamRequest,
  Department,
  Team
} from '../models/organization.model';

@Injectable({
  providedIn: 'root'
})
export class OrganizationService {

  private readonly http = inject(HttpClient);

  private readonly apiUrl =
    environment.apiUrl.replace(/\/+$/, '');

  getCompanies(): Observable<Company[]> {
    return this.http.get<Company[]>(
      `${this.apiUrl}/companies`
    );
  }

  createCompany(
    request: CreateCompanyRequest
  ): Observable<Company> {
    return this.http.post<Company>(
      `${this.apiUrl}/companies`,
      request
    );
  }

  deleteCompany(
    companyId: number
  ): Observable<void> {
    return this.http.delete<void>(
      `${this.apiUrl}/companies/${companyId}`
    );
  }

  getDepartmentsByCompany(
    companyId: number
  ): Observable<Department[]> {
    return this.http.get<Department[]>(
      `${this.apiUrl}/departments/company/${companyId}`
    );
  }

  createDepartment(
    request: CreateDepartmentRequest
  ): Observable<Department> {
    return this.http.post<Department>(
      `${this.apiUrl}/departments`,
      request
    );
  }

  deleteDepartment(
    departmentId: number
  ): Observable<void> {
    return this.http.delete<void>(
      `${this.apiUrl}/departments/${departmentId}`
    );
  }

  getTeamsByDepartment(
    departmentId: number
  ): Observable<Team[]> {
    return this.http.get<Team[]>(
      `${this.apiUrl}/teams/department/${departmentId}`
    );
  }

  createTeam(
    request: CreateTeamRequest
  ): Observable<Team> {
    return this.http.post<Team>(
      `${this.apiUrl}/teams`,
      request
    );
  }

  deleteTeam(
    teamId: number
  ): Observable<void> {
    return this.http.delete<void>(
      `${this.apiUrl}/teams/${teamId}`
    );
  }
}
