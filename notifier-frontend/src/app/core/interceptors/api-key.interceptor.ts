import { HttpInterceptorFn } from '@angular/common/http';

export const apiKeyInterceptor: HttpInterceptorFn = (req, next) => {
  const apiKey = localStorage.getItem('notifier_api_key');
  if (apiKey) {
    const cloned = req.clone({
      setHeaders: { Authorization: `Api-Key ${apiKey}` },
    });
    return next(cloned);
  }
  return next(req);
};
