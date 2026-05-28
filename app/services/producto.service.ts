import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Producto {
  id?: number;
  nombre: string;
  categoria: string;
  precio: number;
  stock: number;
  codigo_barras?: string;
}

@Injectable({ providedIn: 'root' })
export class ProductoService {
  private url = 'http://127.0.0.1:5000';

  constructor(private http: HttpClient) {}

  getAll(): Observable<Producto[]> {
    return this.http.get<Producto[]>(`${this.url}/productos`);
  }

  getOne(id: number): Observable<Producto> {
    return this.http.get<Producto>(`${this.url}/productos/${id}`);
  }

  create(p: Producto): Observable<any> {
    return this.http.post(`${this.url}/productos`, p);
  }

  update(id: number, p: Producto): Observable<any> {
    return this.http.put(`${this.url}/productos/${id}`, p);
  }

  delete(id: number): Observable<any> {
    return this.http.delete(`${this.url}/productos/${id}`);
  }
}
