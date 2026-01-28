import type { NextApiRequest, NextApiResponse } from "next";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
    if (req.method === "GET") {
        res.status(200).json({
            application: "CloudGate",
            version: "3.7.2",
            description: "Enterprise Cloud Management Platform",
            api_version: "v1",
            endpoints: {
                public: {
                    info: "/api/info",
                    health: "/api/health",
                    status: "/api/status",
                    metrics: "/api/metrics"
                },
                auth: {
                    login: "/api/auth",
                    user: "/api/user"
                },
                admin: {
                    protected: "/api/admin/*"
                }
            },
            documentation: "/docs"
        });
    } else {
        res.setHeader("Allow", ["GET"]);
        res.status(405).end(`Method ${req.method} Not Allowed`);
    }
}
