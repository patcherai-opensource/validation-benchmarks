import LoginForm from "../components/LoginForm";
import { cookies } from "next/headers";
import { checkSession } from "../actions/sessionManager";
import { redirect } from "next/navigation";

export default async function Dashboard() {
    const token = cookies().get("token")?.value as string;
    const session = token ? await checkSession(token) : null;
    
    if(session && !session?.error && token !== "") {
        redirect("/dashboard/profile");
    }

    return (
        <div className="dashboard__login">
            {(session?.error || !session) && <LoginForm />}
        </div>
    );
}
