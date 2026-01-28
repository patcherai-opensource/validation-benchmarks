import { getDB } from "./db/sqlite";
import S3Image from "./components/S3Image";

export default async function Home() {
  await getDB();

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
<div className="flex flex-col min-h-screen">
      <main className="container mx-auto px-4 py-10 text-center">
        <h2 className="text-4xl font-bold mb-4">Enterprise Cloud Infrastructure Management</h2>
        <p className="text-xl mb-24 w-1/2 mx-auto mt-12">
        CloudGate provides comprehensive cloud management solutions for modern enterprises. Our platform enables seamless deployment, monitoring, and scaling of your cloud infrastructure with enterprise-grade security.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-24 mb-8">
          <div>

            <S3Image src="/front_image_1.jpeg" alt="" className="w-full h-auto" />
            <p className="mt-8 text-justify">Deploy and manage cloud resources across multiple providers with a unified interface. Our orchestration engine handles complex deployments automatically.</p>
          </div>
          <div>
            <S3Image src="/front_image_2.jpeg" alt="" className="w-full h-auto" />
            <p className="mt-8 text-justify">Real-time monitoring and analytics provide deep insights into your infrastructure performance. Set up alerts and automated responses to maintain optimal uptime.</p>
          </div>
          <div>
            <S3Image src="/front_image_3.jpeg" alt="" className="w-full h-auto" />
            <p className="mt-8 text-justify">Enterprise security with role-based access control, audit logging, and compliance reporting. Meet regulatory requirements with our comprehensive security framework.</p>
          </div>
        </div>
        <button className="bg-black mt-20 text-white border-white border-2 py-4 px-12 rounded text-2xl">
          Request Demo
        </button>
      </main>
      <footer className="text-white py-4">
        <div className="container mx-auto px-4 text-center">
          <p>2024 CloudGate Technologies. All rights reserved.</p>
        </div>
      </footer>
    </div>
    </main>
  );
}
