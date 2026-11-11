import fastify from "fastify";

import {sequelize} from "./src/config/database";

import {clienteRouter} from "./src/router/cliente.router";

const PORT = Number(process.env.PORT) || 3001;
const app = fastify({
    logger:true
});

app.register(clienteRouter, {prefix:"/api"});

const iniciar = async () => {
    try{
        await sequelize.authenticate();
        await sequelize.sync();

        await app.listen({
            port: PORT,
            host:"0.0.0.0"
        });
        console.log("Microservicio cliente ejecutándose en el puerto " + PORT);
    }catch(error){
        app.log.error(error);
        process.exit(1);

    }

};

iniciar();
