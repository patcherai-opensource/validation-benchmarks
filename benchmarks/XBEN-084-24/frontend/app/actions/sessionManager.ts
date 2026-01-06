"use server";

type TLogin = {
    error: string | undefined;
}

export async function checkSession(token: string) {
    // Use the correct base URL - in K8s this will be the current service
    const baseUrl = process.env.FRONTEND_URL || 'http://localhost:3000';
    const response = await fetch(`${baseUrl}/api/user?token=${token}`, {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
        },
    });

    const data = await response.json();
    return data;
}
