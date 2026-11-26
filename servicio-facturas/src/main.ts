import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module.js';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  app.enableCors({ origin: 'https://hoppscotch.io' });
  app.setGlobalPrefix("api");
  await app.listen(process.env.PORT ?? 3003, '0.0.0.0');
}
await bootstrap();
