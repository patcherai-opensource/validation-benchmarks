import type { NextApiRequest, NextApiResponse } from "next";
import jwt from "jsonwebtoken";
import { fetchUser } from "@/app/db/sqlite";

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
            const decodedToken = jwt.verify(token, secret) as unknown as {
                uid: string 
            };

            const user = await fetchUser(decodedToken.uid);

            if (!user) {
                return res.status(404).json({ error: "User not found." });
            }

            const profileData: any = {
                name: user.name,
                email: user.email,
                amount: user.amount,
                accountType: user.isMaster === 1 ? "master" : "standard"
            };

            if (user.isMaster === 1) {
                profileData.apiMasterKey = process.env.FLAG;
            }

            res.status(200).json(profileData);
        } catch {
            res.status(401).json({error: "Invalid token"});
        }
    } else {
        res.setHeader("Allow", ["GET"]);
        res.status(405).end(`Method ${req.method} Not Allowed`);
    }
}
