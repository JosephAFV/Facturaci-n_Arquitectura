import 'dotenv/config';
import { Injectable, NotFoundException, ServiceUnavailableException } from '@nestjs/common';
import type { Producto } from '../models/producto.model.js';

@Injectable()
export class ProductoClienteService {
    private readonly url = process.env['PRODUCTOS_URL'];

    async consultar(codigo: number): Promise<Producto> {
        if (!this.url) {
            throw new ServiceUnavailableException('Configura PRODUCTOS_URL en el .env');
        }
        try {
            const respuesta = await fetch(`${this.url.replace(/\/$/, '')}/${codigo}`, {
                signal: AbortSignal.timeout(5000),
            });
            if (respuesta.status === 404) {
                throw new NotFoundException('Producto no encontrado');
            }
            if (!respuesta.ok) {
                throw new ServiceUnavailableException('Servicio de productos no disponible');
            }
            const producto = await respuesta.json() as Producto;
            if (typeof producto.precio !== 'number' || !Number.isFinite(producto.precio) || producto.precio < 0) {
                throw new ServiceUnavailableException('El servicio de productos devolvió un precio inválido');
            }
            return producto;
        } catch (error) {
            if (error instanceof NotFoundException || error instanceof ServiceUnavailableException) {
                throw error;
            }
            throw new ServiceUnavailableException('No se pudo conectar con el servicio de productos');
        }
    }
}
