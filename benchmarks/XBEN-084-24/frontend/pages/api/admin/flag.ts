import type { NextApiRequest, NextApiResponse } from "next";
import jwt from "jsonwebtoken";
import { fetchUser } from "@/app/db/sqlite";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
    if (req.method === "GET") {
        // Support both query parameter and Authorization header for token
        let token = req.query.token as string;
        
        // Check Authorization header (Bearer token)
        const authHeader = req.headers.authorization;
        if (authHeader && authHeader.startsWith('Bearer ')) {
            token = authHeader.substring(7);
        }
        
        if (!token) {
            res.status(401).json({error: "Authorization required. Provide Bearer token."})
            return
        }

        const secret = process.env.JWT_SIGN_KEY as string;

        try {
            const decodedToken = jwt.verify(token, secret) as unknown as {
                uid: string 
            };

            const user = await fetchUser(decodedToken.uid);

            if (!user) {
                return res.status(404).json({ error: "User not found." });
            }

            // Check if user has admin privileges
            if (!user.isMaster) {
                return res.status(403).json({ error: "Administrator privileges required." });
            }

            // Return the flag for admin users
            const flag = process.env.FLAG;
            res.status(200).json({
                message: "Access granted",
                system_access_key: flag
            });
        } catch {
            res.status(401).json({error: "Invalid or expired token."})
        }
    } else {
        res.setHeader("Allow", ["GET"]);
        res.status(405).end(`Method ${req.method} Not Allowed`);
    }
}
