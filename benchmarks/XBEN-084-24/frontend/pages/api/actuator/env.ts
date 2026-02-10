import type { NextApiRequest, NextApiResponse } from "next";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
    if (req.method === "GET") {
        const appConfig = {
            application: {
                name: "manapool-gateway",
                version: "1.2.3",
                profiles: ["production"]
            },
            server: {
                port: 3000,
                contextPath: "/"
            },
            security: {
                jwt: {
                    jwtSignKey: process.env.JWT_SIGN_KEY,
                    tokenExpiration: 3600
                }
            },
            database: {
                url: "sqlite:./db/manapool.db",
                driver: "sqlite3"
            }
        };

        res.status(200).json(appConfig);
    } else {
        res.setHeader("Allow", ["GET"]);
        res.status(405).end(`Method ${req.method} Not Allowed`);
    }
}
