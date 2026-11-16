import type {FastifyInstance} from "fastify";

import { obtenerClienteId, obtenerClientes, crearCliente, actualizarCliente, eliminarCliente} from "../controllers/cliente.controller";

const camposCliente = ["nombre", "direccion", "telefono"] as const;

function leerCliente(body: unknown) {
    const datos = body as Record<string, unknown> | undefined;
    const cliente = datos && Object.hasOwn(datos, "cliente") ? datos.cliente : datos;
    if (!cliente || typeof cliente !== "object" || Array.isArray(cliente)) {
        return undefined;
    }
    return cliente as Record<string, unknown>;
}

function validarCliente(cliente: Record<string, unknown>, parcial: boolean) {
    const campos = parcial ? camposCliente.filter(campo => Object.hasOwn(cliente, campo)) : camposCliente;
    if (campos.length === 0) {
        return "Envía al menos un campo de cliente";
    }
    for (const campo of campos) {
        const valor = cliente[campo];
        if (typeof valor !== "string" || valor.trim() === "") {
            return parcial
                ? `El campo ${campo} no puede estar vacío`
                : "Nombre, dirección y teléfono son obligatorios";
        }
    }
    if (campos.includes("telefono") && !/^[0-9]{10}$/.test(cliente.telefono as string)) {
        return "El teléfono debe tener exactamente 10 dígitos";
    }
}

export const clienteRouter = async (app: FastifyInstance) => {
    app.get("/clientes", obtenerClientes);

    app.get<{Params: {id: string}}>("/clientes/:id", async (req, res) => {
        try{
            return await obtenerClienteId(Number(req.params.id));
        }catch(error){
            console.log("Error al obtener todos los clientes");
            res.code(400).send({"mensaje":"Error en obtener clientes"});
        }
    });

    app.post<{Body: Record<string, unknown>}>("/clientes", async (req, res) => {
        try{
            const cliente = leerCliente(req.body);
            if (!cliente) {
                return res.code(400).send({"mensaje": "Error al crear clientes"});
            }

            const mensaje = validarCliente(cliente, false);
            if (mensaje) {
                return res.code(400).send({mensaje});
            }

            return await crearCliente(cliente);
        }catch(error){
            console.log("Error al crear clientes");
            res.code(400).send({"mensaje": "Error al crear clientes"});
        }
    });

    app.put<{Params: {id: string}}>("/clientes/:id", async (req, res) => {
        try{
            const cliente = leerCliente(req.body);
            if (!cliente) {
                return res.code(400).send({mensaje: "Error al actualizar clientes"});
            }
            const mensaje = validarCliente(cliente, true);
            if (mensaje) {
                return res.code(400).send({mensaje});
            }
            return await actualizarCliente(Number(req.params.id), cliente);
        }catch(error){
            console.log("Error al actualizar cliente");
            res.code(400).send({"mensaje": "Error al actualizar clientes"});
        }
    });

    app.delete<{Params: {id: string}}>("/clientes/:id", async (req, res) => {
        try{
            return await eliminarCliente(Number(req.params.id));
        }catch(error){
            console.log("Error al eliminar cliente");
            res.code(400).send({"mensaje": "Error al eliminar clientes"});
        }
    });

}
