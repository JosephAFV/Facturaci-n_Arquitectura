import 'dotenv/config';
import {
    Injectable,
    BadRequestException,
    NotFoundException,
    ServiceUnavailableException,
} from '@nestjs/common';

@Injectable()
export class ClienteClienteService {
    private readonly url = process.env['CLIENTES_URL'];

    async validarExistencia(codigo: number): Promise<void> {
        if (!Number.isInteger(codigo) || codigo <= 0) {
            throw new BadRequestException(
                'El código de cliente debe ser un entero positivo',
            );
        }

        if (!this.url) {
            throw new ServiceUnavailableException(
                'Configura CLIENTES_URL en el .env',
            );
        }

        try {
            const respuesta = await fetch(
                `${this.url.replace(/\/$/, '')}/${codigo}`,
                { signal: AbortSignal.timeout(5000) },
            );

            if (respuesta.status === 404) {
                throw new NotFoundException('Cliente no encontrado');
            }

            if (!respuesta.ok) {
                throw new ServiceUnavailableException(
                    'Servicio de clientes no disponible',
                );
            }
        } catch (error) {
            if (
                error instanceof NotFoundException ||
                error instanceof ServiceUnavailableException
            ) {
                throw error;
            }

            throw new ServiceUnavailableException(
                'No se pudo conectar con el servicio de clientes',
            );
        }
    }
}