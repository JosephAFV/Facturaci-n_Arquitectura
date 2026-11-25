import { Module } from '@nestjs/common';
import { FacturaController } from './factura.controller.js';
import { FacturaService } from './factura.service.js';
import { ProductoClienteService } from '../../service/producto-cliente.service.js';
import { ClienteClienteService } from '../../service/cliente-cliente.service.js';

@Module({
  controllers: [FacturaController],
  providers: [FacturaService, ProductoClienteService, ClienteClienteService]
})
export class FacturaModule {}
