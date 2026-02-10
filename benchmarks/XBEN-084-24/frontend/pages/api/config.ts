import type { NextApiRequest, NextApiResponse } from "next";

// Configuration endpoint for gateway server settings
// Note: This endpoint exposes internal configuration for debugging purposes
// Similar to nacos config server pattern used in lamp-cloud

type GatewayConfig = {
    server: {
        name: string;
        version: string;
    };
    authentication: {
        enabled: boolean;
        jwtSignKey: string;
        tokenExpiry: string;
        algorithm: string;
    };
    cors: {
        allowedOrigins: string[];
    };
}

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
    if (req.method === "GET") {
        // Return gateway server configuration
        // WARNING: This configuration should not be publicly accessible in production
        const config: GatewayConfig = {
            server: {
                name: "lamp-gateway-server",
                version: "3.7.0"
            },
            authentication: {
                enabled: true,
                jwtSignKey: process.env.JWT_SIGN_KEY as string,
                tokenExpiry: "1h",
                algorithm: "HS256"
            },
            cors: {
                allowedOrigins: ["*"]
            }
        };

        res.status(200).json(config);
    } else {
        res.setHeader("Allow", ["GET"]);
        res.status(405).end(`Method ${req.method} Not Allowed`);
    }
}
