import { Injectable, NotFoundException, ConflictException, BadRequestException } from '@nestjs/common';
import type { Factura } from '../../models/factura.model.js';
import type { DetalleFactura } from '../../models/detalle-factura.models.js';
import { db } from '../../prisma/db.js';
import { ProductoClienteService } from '../../service/producto-cliente.service.js';
import { ClienteClienteService } from '../../service/cliente-cliente.service.js';

@Injectable()
export class FacturaService {
    constructor(
        private readonly productoCliente: ProductoClienteService,
        private readonly clienteCliente: ClienteClienteService,
    ) { }

    private async detalleConSubtotal(data: Omit<DetalleFactura, 'Subtotal'>): Promise<DetalleFactura> {
        if (!Number.isInteger(data.cod_producto) || data.cod_producto <= 0) {
            throw new BadRequestException('El código de producto debe ser un entero positivo');
        }
        if (!Number.isInteger(data.cantidad) || data.cantidad <= 0) {
            throw new BadRequestException('La cantidad debe ser un entero positivo');
        }
        const producto = await this.productoCliente.consultar(data.cod_producto);
        const subtotal = Math.round(producto.precio * data.cantidad * 100) / 100;
        if (!Number.isFinite(subtotal)) {
            throw new BadRequestException('El subtotal excede el valor permitido');
        }
        return { ...data, Subtotal: subtotal };
    }

    async crear(data: Factura) {
        await this.clienteCliente.validarExistencia(data.cod_cliente);
        const factura = await db.orm.Factura.where({ Codigo: data.codigo }).first();
        if (factura) {
            throw new ConflictException("Codigo ya existente");
        }
        const { codigo, fecha, ...datos } = data;
        const fechaFactura = new Date(fecha);
        if (Number.isNaN(fechaFactura.getTime())) {
            throw new BadRequestException('Fecha inválida');
        }
        const detalles = await Promise.all(datos.detalles_factura.map(d => this.detalleConSubtotal(d)));
        return db.orm.Factura.create({ ...datos, Codigo: codigo, fecha: fechaFactura, detalles_factura: detalles });
    }

    async listar() {
        return db.orm.Factura.all();
    }

    async consultar(codigo: string) {
        const factura = await db.orm.Factura
            .where({ Codigo: codigo })
            .first();
        if (!factura) {
            throw new NotFoundException('Factura no encontrada');
        }
        return factura;
    }

    async actualizar(codigo: string, data: Partial<Factura>) {
        const { codigo: nuevoCodigo, fecha, ...datos } = data;
        const cambios = {
            ...datos,
            ...(nuevoCodigo !== undefined ? { Codigo: nuevoCodigo } : {}),
            ...(fecha !== undefined ? { fecha: new Date(fecha) } : {}),
        };
        if (cambios.fecha && Number.isNaN(cambios.fecha.getTime())) {
            throw new BadRequestException('Fecha inválida');
        }
        if (cambios.detalles_factura !== undefined) {
            cambios.detalles_factura = await Promise.all(
                cambios.detalles_factura.map(d => this.detalleConSubtotal(d)),
            );
        }
        const factura = await db.orm.Factura.where({ Codigo: codigo }).update(cambios);

        if (!factura) {
            throw new NotFoundException("factura no encontrada");

        }
        return factura;
    }

    async eliminar(codigo: string) {
        const factura = await db.orm.Factura.where({ Codigo: codigo }).delete();
        if (!factura) {
            throw new NotFoundException('Factura no encontrada');
        }
        return { mensaje: `Factura eliminada correctamente` };
    }


    //detalle de factura
    async agregarDetalle(codigo: string, data: Omit<DetalleFactura, 'Subtotal'>) {
        await this.consultar(codigo);
        const detalle = await this.detalleConSubtotal(data);
        const factura = await db.orm.Factura.where({ Codigo: codigo }).update((f) => [f.detalles_factura.push(detalle)]);

        if (!factura) {
            throw new NotFoundException('Factura no encontrada');
        }

        return factura;
    }

    // ACTUALIZAR DETALLE
    async actualizarDetalle(
        codigo: string,
        codigoDetalle: number,
        data: Partial<Pick<DetalleFactura, 'cod_producto' | 'cantidad'>>,
    ) {
        const factura = await this.consultar(codigo);

        const detalle = factura.detalles_factura.find(d => d.codigo === codigoDetalle);
        if (!detalle) {
            throw new NotFoundException('Detalle no encontrado');
        }

        if (data.cod_producto === undefined && data.cantidad === undefined) {
            throw new BadRequestException('Envía cod_producto o cantidad');
        }
        const actualizado = await this.detalleConSubtotal({
            ...detalle,
            cod_producto: data.cod_producto === undefined ? detalle.cod_producto : data.cod_producto,
            cantidad: data.cantidad === undefined ? detalle.cantidad : data.cantidad,
        });
        const detalles = factura.detalles_factura.map(d =>
            d.codigo === codigoDetalle ? actualizado : d,
        );

        return db.orm.Factura
            .where({ Codigo: codigo })
            .update({ detalles_factura: detalles });
    }

    // ELIMINAR DETALLE
    async eliminarDetalle(codigo: string, codigoDetalle: number) {
        const factura = await this.consultar(codigo);

        const detalles = factura.detalles_factura.filter(
            d => d.codigo !== codigoDetalle,
        );

        if (detalles.length === factura.detalles_factura.length) {
            throw new NotFoundException('Detalle no encontrado');
        }

        return db.orm.Factura
            .where({ Codigo: codigo })
            .update({ detalles_factura: detalles });
    }

    // CALCULAR SUBTOTAL DE LA FACTURA


    // CALCULAR SUBTOTAL DE LA FACTURA
    async calcularSubtotal(codigo: string) {
        const factura = await this.consultar(codigo);

        return factura.detalles_factura.reduce(
            (suma, detalle) => suma + detalle.Subtotal,
            0,
        );
    }
}
























