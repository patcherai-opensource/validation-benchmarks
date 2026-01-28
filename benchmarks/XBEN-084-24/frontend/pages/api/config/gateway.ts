import type { NextApiRequest, NextApiResponse } from "next";
import path from "path";
import fs from "fs";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
    if (req.method === "GET") {
        // Serve the gateway configuration file
        const configPath = path.join(process.cwd(), 'config', 'cloudgate-gateway-server.yml');
        
        try {
            const configContent = fs.readFileSync(configPath, 'utf-8');
            res.setHeader('Content-Type', 'text/yaml');
            res.status(200).send(configContent);
        } catch (error) {
            res.status(404).json({ error: "Configuration file not found" });
        }
    } else {
        res.setHeader("Allow", ["GET"]);
        res.status(405).end(`Method ${req.method} Not Allowed`);
    }
}
