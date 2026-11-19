import { Body, Controller, Delete, Get, Param, ParseIntPipe, Patch, Post } from '@nestjs/common';
import type { Factura } from '../../models/factura.model.js';
import type { DetalleFactura } from '../../models/detalle-factura.models.js';
import { FacturaService } from './factura.service.js';

@Controller('factura')
export class FacturaController {
    constructor(private readonly facturaService: FacturaService) {}

    @Post()
    crear(@Body() data: Factura) {
        return this.facturaService.crear(data);
    }

    @Get()
    listar() {
        return this.facturaService.listar();
    }

    @Get(':codigo')
    consultar(@Param('codigo') codigo: string) {
        return this.facturaService.consultar(codigo);
    }

    @Patch(':codigo')
    actualizar(@Param('codigo') codigo: string, @Body() data: Partial<Factura>) {
        return this.facturaService.actualizar(codigo, data);
    }

    @Delete(':codigo')
    eliminar(@Param('codigo') codigo: string) {
        return this.facturaService.eliminar(codigo);
    }

    @Post(':codigo/detalles')
    agregarDetalle(@Param('codigo') codigo: string, @Body() data: Omit<DetalleFactura, 'Subtotal'>) {
        return this.facturaService.agregarDetalle(codigo, data);
    }

    @Patch(':codigo/detalles/:codigoDetalle')
    actualizarDetalle(
        @Param('codigo') codigo: string,
        @Param('codigoDetalle', ParseIntPipe) codigoDetalle: number,
        @Body() data: Partial<Pick<DetalleFactura, 'cod_producto' | 'cantidad'>>,
    ) {
        return this.facturaService.actualizarDetalle(codigo, codigoDetalle, data);
    }

    @Delete(':codigo/detalles/:codigoDetalle')
    eliminarDetalle(
        @Param('codigo') codigo: string,
        @Param('codigoDetalle', ParseIntPipe) codigoDetalle: number,
    ) {
        return this.facturaService.eliminarDetalle(codigo, codigoDetalle);
    }

    @Get(':codigo/subtotal')
    calcularSubtotal(@Param('codigo') codigo: string) {
        return this.facturaService.calcularSubtotal(codigo);
    }
}
