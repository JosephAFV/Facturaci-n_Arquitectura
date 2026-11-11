import type {FastifyInstance} from "fastify";

import { obtenerClienteId, obtenerClientes, crearCliente, actualizarCliente, eliminarCliente} from "../controllers/cliente.controller";


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
            const {body} = req;
            const cliente = body && Object.hasOwn(body, "cliente") ? body.cliente : body;
            if (!cliente || typeof cliente !== "object" || Array.isArray(cliente)) {
                return res.code(400).send({"mensaje": "Error al crear clientes"});
            }

            const { nombre, direccion, telefono } = cliente as {
                nombre?: unknown;
                direccion?: unknown;
                telefono?: unknown;
            };

            if(
                typeof nombre !== "string" || nombre.trim() === "" ||
                typeof direccion !== "string" || direccion.trim() === "" ||
                typeof telefono !== "string" || telefono.trim() === ""
            ){
                return res.code(400).send({
                    mensaje: "Nombre, dirección y teléfono son obligatorios",
                });
            }

            if (!/^[0-9]{10}$/.test(telefono)) {
                return res.code(400).send({
                    mensaje: "El teléfono debe tener exactamente 10 dígitos",
                });
            }

            return await crearCliente(cliente);
        }catch(error){
            console.log("Error al crear clientes");
            res.code(400).send({"mensaje": "Error al crear clientes"});
        }
    });

    app.put<{Params: {id: string}}>("/clientes/:id", async (req, res) => {
        try{
            const {cliente} = req.body as {cliente: Record<string, unknown>};
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
