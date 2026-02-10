import type { NextApiRequest, NextApiResponse } from "next";
import { getDB } from "@/app/db/sqlite";

// User listing endpoint - returns basic user information
// Public endpoint for user directory (misconfigured - should require authentication)

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
    if (req.method === "GET") {
        try {
            const db = await getDB();
            const users = await db.all("SELECT uid, name, email, isMaster FROM users");
            
            return res.status(200).json({
                users: users.map(u => ({
                    uid: u.uid,
                    name: u.name,
                    email: u.email,
                    role: u.isMaster ? "master" : "user"
                }))
            });
        } catch (error) {
            return res.status(500).json({ 
                error: "Internal server error"
            });
        }
    } else {
        res.setHeader("Allow", ["GET"]);
        res.status(405).end(`Method ${req.method} Not Allowed`);
    }
}
