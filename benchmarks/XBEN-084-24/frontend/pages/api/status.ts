import type { NextApiRequest, NextApiResponse } from "next";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
    if (req.method === "GET") {
        res.status(200).json({
            status: "operational",
            uptime: Math.floor(Math.random() * 100000) + 50000,
            region: "us-west-2",
            cluster: "production-1"
        });
    } else {
        res.setHeader("Allow", ["GET"]);
        res.status(405).end(`Method ${req.method} Not Allowed`);
    }
}
