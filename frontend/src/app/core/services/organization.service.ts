import { HttpClient } from '@angular/common/http';
import {
  Injectable,
  inject
} from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';

import {
  Company,
  CreateDepartmentRequest,
  CreateTeamRequest,
  Department,
  Team,
  UpdateCompanyRequest,
  UpdateDepartmentRequest,
  UpdateTeamRequest
} from '../models/organization.model';


@Injectable({
  providedIn: 'root'
})
export class OrganizationService {

  private readonly http = inject(HttpClient);

  private readonly apiUrl =
    environment.apiUrl.replace(/\/+$/, '');

  getMyCompany(): Observable<Company> {
    return this.http.get<Company>(
      `${this.apiUrl}/companies/me`
    );
  }

  updateMyCompany(
    request: UpdateCompanyRequest
  ): Observable<Company> {
    return this.http.put<Company>(
      `${this.apiUrl}/companies/me`,
      request
    );
  }

  getDepartments(): Observable<Department[]> {
    return this.http.get<Department[]>(
      `${this.apiUrl}/departments`
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

  updateDepartment(
    departmentId: number,
    request: UpdateDepartmentRequest
  ): Observable<Department> {
    return this.http.put<Department>(
      `${this.apiUrl}/departments/${departmentId}`,
      request
    );
  }

  activateDepartment(
    departmentId: number
  ): Observable<Department> {
    return this.http.patch<Department>(
      `${this.apiUrl}/departments/${departmentId}/activate`,
      {}
    );
  }

  deactivateDepartment(
    departmentId: number
  ): Observable<Department> {
    return this.http.patch<Department>(
      `${this.apiUrl}/departments/${departmentId}/deactivate`,
      {}
    );
  }

  deleteDepartment(
    departmentId: number
  ): Observable<void> {
    return this.http.delete<void>(
      `${this.apiUrl}/departments/${departmentId}`
    );
  }

  getTeams(): Observable<Team[]> {
    return this.http.get<Team[]>(
      `${this.apiUrl}/teams`
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

  updateTeam(
    teamId: number,
    request: UpdateTeamRequest
  ): Observable<Team> {
    return this.http.put<Team>(
      `${this.apiUrl}/teams/${teamId}`,
      request
    );
  }

  activateTeam(
    teamId: number
  ): Observable<Team> {
    return this.http.patch<Team>(
      `${this.apiUrl}/teams/${teamId}/activate`,
      {}
    );
  }

  deactivateTeam(
    teamId: number
  ): Observable<Team> {
    return this.http.patch<Team>(
      `${this.apiUrl}/teams/${teamId}/deactivate`,
      {}
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
