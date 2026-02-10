import type { NextApiRequest, NextApiResponse } from "next";
import jwt from "jsonwebtoken";
import { getDB } from "@/app/db/sqlite";

function extractToken(req: NextApiRequest): string | null {
    const authHeader = req.headers.authorization;
    if (authHeader && authHeader.startsWith('Bearer ')) {
        return authHeader.substring(7);
    }
    if (req.query.token) {
        return req.query.token as string;
    }
    return null;
}

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
    if (req.method === "GET") {
        const token = extractToken(req);
        
        if (!token) {
            res.status(401).json({error: "Unauthorized"});
            return;
        }

        const secret = process.env.JWT_SIGN_KEY as string;

        try {
            jwt.verify(token, secret);
            
            const db = await getDB();
            const users = await db.all("SELECT uid, name, email, isMaster FROM users");
            
            res.status(200).json({ users });
        } catch {
            res.status(401).json({error: "Invalid token"});
        }
    } else {
        res.setHeader("Allow", ["GET"]);
        res.status(405).end(`Method ${req.method} Not Allowed`);
    }
}
