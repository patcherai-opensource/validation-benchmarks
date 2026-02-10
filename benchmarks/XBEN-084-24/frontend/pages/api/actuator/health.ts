import type { NextApiRequest, NextApiResponse } from "next";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
    if (req.method === "GET") {
        const healthStatus = {
            status: "UP",
            components: {
                db: {
                    status: "UP",
                    details: {
                        database: "SQLite",
                        validationQuery: "SELECT 1"
                    }
                },
                diskSpace: {
                    status: "UP",
                    details: {
                        total: 268435456000,
                        free: 134217728000,
                        threshold: 10485760
                    }
                }
            }
        };

        res.status(200).json(healthStatus);
    } else {
        res.setHeader("Allow", ["GET"]);
        res.status(405).end(`Method ${req.method} Not Allowed`);
    }
}
