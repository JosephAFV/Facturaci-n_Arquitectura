import { Test, TestingModule } from '@nestjs/testing';
import { FacturaController } from './factura.controller.js';
import { FacturaService } from './factura.service.js';

describe('FacturaController', () => {
  let controller: FacturaController;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      controllers: [FacturaController],
      providers: [{ provide: FacturaService, useValue: {} }],
    }).compile();

    controller = module.get<FacturaController>(FacturaController);
  });

  it('should be defined', () => {
    expect(controller).toBeDefined();
  });
});
