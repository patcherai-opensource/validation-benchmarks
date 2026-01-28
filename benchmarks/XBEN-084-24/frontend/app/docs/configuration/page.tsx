export default async function ConfigurationPage() {
    return (
        <main className="flex-grow container mx-auto px-4 py-24 text-center pt-24">
        <section className="mb-16 text-left max-w-4xl mx-auto">
          <h2 className="text-4xl font-bold mb-8">Configuration</h2>
          
          <h3 className="text-2xl font-bold mb-4">Server Configuration</h3>
          <p className="mb-6">CloudGate uses YAML-based configuration files for server setup.</p>
          
          <h4 className="text-xl font-bold mb-2">Configuration Files</h4>
          <p className="mb-4">The main configuration files are:</p>
          <ul className="list-disc ml-8 mb-6">
            <li><code>cloudgate-gateway-server.yml</code> - Gateway server configuration</li>
            <li><code>cloudgate-oauth-server.yml</code> - OAuth server configuration</li>
          </ul>
          
          <h4 className="text-xl font-bold mb-2">Environment Variables</h4>
          <p className="mb-4">Key environment variables:</p>
          <ul className="list-disc ml-8 mb-6">
            <li><code>JWT_SIGN_KEY</code> - JWT signing key (required)</li>
            <li><code>FRONTEND_URL</code> - Frontend service URL</li>
          </ul>
          
          <div className="bg-yellow-900 p-4 rounded mb-6">
            <p className="font-bold">Security Warning</p>
            <p>Always change default configuration values, especially authentication-related settings, before deploying to production.</p>
          </div>
        </section>
      </main>
    );
}
