import type { NextApiRequest, NextApiResponse } from "next";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
    if (req.method === "GET") {
        res.status(200).json({
            status: "UP",
            timestamp: new Date().toISOString(),
            version: "3.7.2",
            services: {
                database: "UP",
                gateway: "UP",
                authentication: "UP"
            }
        });
    } else {
        res.setHeader("Allow", ["GET"]);
        res.status(405).end(`Method ${req.method} Not Allowed`);
    }
}
