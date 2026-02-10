import type { NextApiRequest, NextApiResponse } from "next";
import jwt from "jsonwebtoken";
import { fetchUser } from "@/app/db/sqlite";

// Protected admin endpoint to retrieve sensitive data
// Requires valid JWT token with master privileges

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
    if (req.method === "GET") {
        // Support both Authorization header and query parameter
        let token: string | undefined;
        
        const authHeader = req.headers.authorization;
        if (authHeader && authHeader.startsWith('Bearer ')) {
            token = authHeader.substring(7);
        } else if (req.query.token) {
            token = req.query.token as string;
        }
        
        if (!token) {
            return res.status(401).json({ 
                error: "Unauthorized",
                message: "JWT token required. Use Authorization: Bearer <token> header or ?token=<token> query parameter"
            });
        }

        const secret = process.env.JWT_SIGN_KEY as string;

        try {
            const decodedToken = jwt.verify(token, secret) as { uid: string };
            const user = await fetchUser(decodedToken.uid);

            if (!user) {
                return res.status(404).json({ error: "User not found" });
            }

            // Only master users can access the flag
            if (!user.isMaster) {
                return res.status(403).json({ 
                    error: "Forbidden",
                    message: "Only master users can access this resource"
                });
            }

            // Return the flag for master users
            const flag = process.env.FLAG;
            return res.status(200).json({
                message: "Access granted",
                user: {
                    name: user.name,
                    email: user.email,
                    role: "master"
                },
                flag: flag
            });
        } catch (error) {
            return res.status(401).json({ 
                error: "Invalid token",
                message: "JWT verification failed"
            });
        }
    } else {
        res.setHeader("Allow", ["GET"]);
        res.status(405).end(`Method ${req.method} Not Allowed`);
    }
}
