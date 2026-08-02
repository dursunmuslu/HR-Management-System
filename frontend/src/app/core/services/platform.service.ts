import { HttpClient } from '@angular/common/http';

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
  CompanyCreationResponse,
  CompanyStatusResponse,
  CreateCompanyWithAdminRequest,
  PlatformCompany,
  PlatformSummary,
  SuspendCompanyRequest
} from '../models/platform.model';


@Injectable({
  providedIn: 'root'
})
export class PlatformService {

  private readonly http =
    inject(HttpClient);

  private readonly apiUrl =
    environment.apiUrl.replace(/\/+$/, '');

  private readonly platformApiUrl =
    `${this.apiUrl}/platform`;


  getSummary():
    Observable<PlatformSummary> {

    return this.http.get<PlatformSummary>(
      `${this.platformApiUrl}/summary`
    );
  }


  getCompanies():
    Observable<PlatformCompany[]> {

    return this.http.get<PlatformCompany[]>(
      `${this.platformApiUrl}/companies`
    );
  }


  createCompany(
    request: CreateCompanyWithAdminRequest
  ): Observable<CompanyCreationResponse> {

    return this.http.post<CompanyCreationResponse>(
      `${this.platformApiUrl}/companies`,
      request
    );
  }


  suspendCompany(
    companyId: number,
    request: SuspendCompanyRequest
  ): Observable<CompanyStatusResponse> {

    return this.http.patch<CompanyStatusResponse>(
      `${this.platformApiUrl}/companies/${companyId}/suspend`,
      request
    );
  }


  activateCompany(
    companyId: number
  ): Observable<CompanyStatusResponse> {

    return this.http.patch<CompanyStatusResponse>(
      `${this.platformApiUrl}/companies/${companyId}/activate`,
      {}
    );
  }
}
