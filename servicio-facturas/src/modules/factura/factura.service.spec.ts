import { Test, TestingModule } from '@nestjs/testing';
import { FacturaService } from './factura.service.js';
import { ProductoClienteService } from '../../service/producto-cliente.service.js';
import { ClienteClienteService } from '../../service/cliente-cliente.service.js';

describe('FacturaService', () => {
  let service: FacturaService;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        FacturaService,
        { provide: ProductoClienteService, useValue: { consultar: vi.fn() } },
        { provide: ClienteClienteService, useValue: { validarExistencia: vi.fn() } },
      ],
    }).compile();

    service = module.get<FacturaService>(FacturaService);
  });

  it('should be defined', () => {
    expect(service).toBeDefined();
  });
});
