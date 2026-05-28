import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class VentaService {
  private url = 'http://127.0.0.1:5000';

  constructor(private http: HttpClient) {}

  getAll(): Observable<any[]> {
    return this.http.get<any[]>(`${this.url}/ventas`);
  }

  create(venta: any): Observable<any> {
    return this.http.post(`${this.url}/ventas`, venta);
  }

  getDashboard(): Observable<any> {
    return this.http.get(`${this.url}/dashboard`);
  }

  getInventario(): Observable<any[]> {
    return this.http.get<any[]>(`${this.url}/inventario`);
  }
}
