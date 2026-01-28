import Link from "next/link";

export default async function DocsPage() {
    return (
        <main className="flex-grow container mx-auto px-4 py-24 text-center pt-24">
        <section className="mb-16">
          <h2 className="text-4xl font-bold mb-4">Documentation</h2>
          <p className="text-xl mb-8">Technical documentation and API references for CloudGate platform.</p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mt-12 max-w-4xl mx-auto">
            <Link href="/docs/getting-started" className="bg-gray-800 p-6 rounded-lg text-left hover:bg-gray-700">
              <h3 className="text-2xl font-bold mb-4">Getting Started</h3>
              <p>Quick start guide for setting up CloudGate in your environment.</p>
            </Link>
            
            <Link href="/docs/api-reference" className="bg-gray-800 p-6 rounded-lg text-left hover:bg-gray-700">
              <h3 className="text-2xl font-bold mb-4">API Reference</h3>
              <p>Complete API documentation with authentication details and examples.</p>
            </Link>
            
            <Link href="/docs/configuration" className="bg-gray-800 p-6 rounded-lg text-left hover:bg-gray-700">
              <h3 className="text-2xl font-bold mb-4">Configuration</h3>
              <p>Server configuration options and deployment settings.</p>
            </Link>
            
            <Link href="/docs/security" className="bg-gray-800 p-6 rounded-lg text-left hover:bg-gray-700">
              <h3 className="text-2xl font-bold mb-4">Security Guide</h3>
              <p>Security best practices and authentication mechanisms.</p>
            </Link>
          </div>
        </section>
        <footer className="text-white py-4">
            <div className="container mx-auto px-4 text-center">
            <p>2024 CloudGate Technologies. All rights reserved.</p>
            </div>
         </footer>
      </main>
    );
}
