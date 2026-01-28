export default async function GettingStartedPage() {
    return (
        <main className="flex-grow container mx-auto px-4 py-24 text-center pt-24">
        <section className="mb-16 text-left max-w-4xl mx-auto">
          <h2 className="text-4xl font-bold mb-8">Getting Started</h2>
          
          <h3 className="text-2xl font-bold mb-4">Quick Start Guide</h3>
          <p className="mb-6">Welcome to CloudGate. This guide will help you get started with our platform.</p>
          
          <h4 className="text-xl font-bold mb-2">1. Authentication</h4>
          <p className="mb-4">CloudGate uses JWT-based authentication. To access protected resources, you need to:</p>
          <ul className="list-disc ml-8 mb-6">
            <li>Login via the /dashboard endpoint or POST to /api/auth</li>
            <li>Include the received token in your requests</li>
            <li>Use the Authorization: Bearer header format</li>
          </ul>
          
          <h4 className="text-xl font-bold mb-2">2. API Endpoints</h4>
          <p className="mb-4">Check the /api/info endpoint for available API endpoints.</p>
          
          <h4 className="text-xl font-bold mb-2">3. Dashboard Access</h4>
          <p className="mb-4">Access the management dashboard at /dashboard after authentication.</p>
        </section>
      </main>
    );
}
