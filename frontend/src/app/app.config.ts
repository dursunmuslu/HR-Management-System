import {
  ApplicationConfig,
  provideZoneChangeDetection
} from '@angular/core';
import {
  provideHttpClient,
  withFetch,
  withInterceptors
} from '@angular/common/http';
import {
  provideClientHydration,
  withEventReplay
} from '@angular/platform-browser';
import {
  provideRouter
} from '@angular/router';

import { routes } from './app.routes';
import {
  authInterceptor
} from './core/interceptors/auth.interceptor';


export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({
      eventCoalescing: true
    }),

    provideRouter(routes),

    provideClientHydration(
      withEventReplay()
    ),

    provideHttpClient(
      withFetch(),
      withInterceptors([
        authInterceptor
      ])
    )
  ]
};
