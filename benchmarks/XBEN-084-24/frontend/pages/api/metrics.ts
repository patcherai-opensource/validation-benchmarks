import type { NextApiRequest, NextApiResponse } from "next";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
    if (req.method === "GET") {
        res.status(200).json({
            cpu_usage: Math.random() * 30 + 10,
            memory_usage: Math.random() * 40 + 20,
            active_connections: Math.floor(Math.random() * 100) + 50,
            requests_per_second: Math.floor(Math.random() * 1000) + 100
        });
    } else {
        res.setHeader("Allow", ["GET"]);
        res.status(405).end(`Method ${req.method} Not Allowed`);
    }
}
