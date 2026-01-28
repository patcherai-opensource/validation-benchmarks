export default async function ApiReferencePage() {
    return (
        <main className="flex-grow container mx-auto px-4 py-24 text-center pt-24">
        <section className="mb-16 text-left max-w-4xl mx-auto">
          <h2 className="text-4xl font-bold mb-8">API Reference</h2>
          
          <div className="mb-8">
            <h3 className="text-2xl font-bold mb-4">Authentication</h3>
            <div className="bg-gray-800 p-4 rounded mb-4">
              <code className="text-green-400">POST /api/auth</code>
              <p className="mt-2 text-gray-300">Authenticate and receive an access token.</p>
              <pre className="mt-2 text-sm">{`Body: { "email": "user@example.com", "password": "..." }`}</pre>
            </div>
          </div>
          
          <div className="mb-8">
            <h3 className="text-2xl font-bold mb-4">User Info</h3>
            <div className="bg-gray-800 p-4 rounded mb-4">
              <code className="text-green-400">GET /api/user</code>
              <p className="mt-2 text-gray-300">Get current user information.</p>
              <pre className="mt-2 text-sm">Header: Authorization: Bearer &lt;token&gt;</pre>
            </div>
          </div>
          
          <div className="mb-8">
            <h3 className="text-2xl font-bold mb-4">Health & Status</h3>
            <div className="bg-gray-800 p-4 rounded mb-4">
              <code className="text-green-400">GET /api/health</code>
              <p className="mt-2 text-gray-300">Check service health status.</p>
            </div>
            <div className="bg-gray-800 p-4 rounded mb-4">
              <code className="text-green-400">GET /api/info</code>
              <p className="mt-2 text-gray-300">Get API information and available endpoints.</p>
            </div>
          </div>
        </section>
      </main>
    );
}
