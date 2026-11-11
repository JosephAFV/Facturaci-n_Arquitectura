import {DataTypes} from "sequelize";
import {sequelize} from "../config/database";

export const Cliente = sequelize.define("Medico", {
    codigo: {
        type: DataTypes.INTEGER,
        primaryKey: true,
        autoIncrement: true
    },
    nombre: {
        type: DataTypes.STRING,
    },
    direccion: {
        type: DataTypes.STRING,
    },  
    telefono: {
        type: DataTypes.STRING,
    }
}
    , {
        tableName:"medico",
        timestamps: false
    }

);
