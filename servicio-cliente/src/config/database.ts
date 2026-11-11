import {Sequelize} from "sequelize";
import dotenv from "dotenv";

dotenv.config();

export const sequelize = new Sequelize(
    process.env.DB_NAME as string,
    process.env.DB_USERNAME as string,
    process.env.DB_PASSWORD ?? process.env.BD_PASSWORD, {
        host: process.env.DB_HOST,
        dialect:"postgres"
    }
)
