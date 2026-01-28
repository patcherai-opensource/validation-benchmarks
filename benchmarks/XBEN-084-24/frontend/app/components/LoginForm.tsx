"use client"

import { useState } from "react";
import { useRouter } from "next/navigation";
import axios from "axios";
import Cookies from "js-cookie";

export default function LoginForm() {
    const router = useRouter();
    const [formData, setFormData] = useState({
        email: "",
        password: ""
    });
    const [error, setError] = useState<string | null>(null);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = async () => {
        try {
            const response = await axios.post("/api/auth", formData, {headers: { "Content-Type": "application/json" }});
            
            if (response.data && response.data.access_token) {
                console.log("Login successful!");
                setError(null);
                Cookies.set("token", response.data.access_token, {expires: 7})
                router.push("/dashboard/profile");
            } 
        } catch(e) {
            setError("Authentication failed. Please verify your credentials.");
        }
    };

    return (
        <div className="flex flex-col items-center justify-center h-screen">
            <h2 className="text-2xl font-bold text-center mb-6">CloudGate Portal</h2>
            <div className="mb-4 w-full max-w-xs">
                <input
                    className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 mb-3 leading-tight focus:outline-none focus:shadow-outline"
                    type="text"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    required
                    placeholder="E-mail"
                />
            </div>
            <div className="mb-6 w-full max-w-xs">
                <input
                    className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 mb-3 leading-tight focus:outline-none focus:shadow-outline"
                    type="password"
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
                    required
                    placeholder="Password"
                />
            </div>
            <div className="mb-10 text-red-400 w-full max-w-xs">
                {error && <p>{error}</p>}
            </div>
            <div className="flex items-center justify-center w-full max-w-xs">
                <button
                    onClick={handleSubmit}
                    className="bg-black border-2 border-white hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                >
                    Sign In
                </button>
            </div>
        </div>
    );
}
