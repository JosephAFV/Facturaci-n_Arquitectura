import {Cliente} from "../models/cliente.model";

export const obtenerClientes = async () => {
    return Cliente.findAll();
}


export const obtenerClienteId = async (id: number) => {
    const cliente = await Cliente.findByPk(id);

    if(!cliente){
        throw new Error("Cliente no encontrado");
        
    }
    return cliente;
} 

export const crearCliente = async(data: any) => {
    if(!data){
        throw Error("Datos Incorrectos");
    }
    return Cliente.create(data);
}

export const actualizarCliente = async(id: number, data: any) => {
    const cliente = await Cliente.findByPk(id);
    if(!cliente){
        throw Error("Cliente no econtrado");
    }
    await cliente.update(data)
    return cliente;
}


export const eliminarCliente = async(id: number) => {
    const cliente = await Cliente.findByPk(id);
    if(!cliente){
        throw Error("Cliente no econtrado");
    }
    await cliente.destroy()
    return {mensaje: "Eliminado Correctamente"};
}
