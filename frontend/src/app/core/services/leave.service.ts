import {
  HttpClient
} from '@angular/common/http';

import {
  Injectable,
  inject
} from '@angular/core';

import {
  Observable
} from 'rxjs';

import {
  environment
} from '../../../environments/environment';

import {
  CreateLeaveRequest,
  LeaveActionRequest,
  LeaveBalance,
  LeaveRequest
} from '../models/leave.model';


@Injectable({
  providedIn: 'root'
})
export class LeaveService {

  private readonly http = inject(HttpClient);

  private readonly apiUrl =
    environment.apiUrl.replace(/\/+$/, '');

  /*
   * Personelin kendi izin talepleri.
   *
   * Backend:
   * GET /leave/my-leaves
   */
  getMyLeaves(): Observable<LeaveRequest[]> {
    return this.http.get<LeaveRequest[]>(
      `${this.apiUrl}/leave/my-leaves`
    );
  }

  /*
   * Yönetici için tüm izin talepleri.
   *
   * Backend:
   * GET /leave
   */
  getAllLeaves(): Observable<LeaveRequest[]> {
    return this.http.get<LeaveRequest[]>(
      `${this.apiUrl}/leave`
    );
  }

  /*
   * Yalnızca bekleyen izin talepleri.
   *
   * Backend:
   * GET /leave/pending
   */
  getPendingLeaves(): Observable<LeaveRequest[]> {
    return this.http.get<LeaveRequest[]>(
      `${this.apiUrl}/leave/pending`
    );
  }

  /*
   * Yeni izin talebi.
   *
   * Backend "reason" değil "description" bekliyor.
   */
  createLeave(
    request: CreateLeaveRequest
  ): Observable<LeaveRequest> {
    return this.http.post<LeaveRequest>(
      `${this.apiUrl}/leave`,
      request
    );
  }

  /*
   * Backend:
   * DELETE /leave/{leaveId}
   */
  cancelLeave(
    leaveId: number
  ): Observable<LeaveRequest> {
    return this.http.delete<LeaveRequest>(
      `${this.apiUrl}/leave/${leaveId}`
    );
  }

  /*
   * Backend:
   * PUT /leave/{leaveId}/approve
   */
  approveLeave(
    leaveId: number,
    request: LeaveActionRequest
  ): Observable<LeaveRequest> {
    return this.http.put<LeaveRequest>(
      `${this.apiUrl}/leave/${leaveId}/approve`,
      request
    );
  }

  /*
   * Backend:
   * PUT /leave/{leaveId}/reject
   */
  rejectLeave(
    leaveId: number,
    request: LeaveActionRequest
  ): Observable<LeaveRequest> {
    return this.http.put<LeaveRequest>(
      `${this.apiUrl}/leave/${leaveId}/reject`,
      request
    );
  }

  /*
   * Personelin kalan yıllık izin bakiyesi.
   */
  getLeaveBalance(): Observable<LeaveBalance> {
    return this.http.get<LeaveBalance>(
      `${this.apiUrl}/employees/me/leave-balance`
    );
  }
}
