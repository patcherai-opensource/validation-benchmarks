export default async function SecurityPage() {
    return (
        <main className="flex-grow container mx-auto px-4 py-24 text-center pt-24">
        <section className="mb-16 text-left max-w-4xl mx-auto">
          <h2 className="text-4xl font-bold mb-8">Security Guide</h2>
          
          <h3 className="text-2xl font-bold mb-4">Authentication</h3>
          <p className="mb-6">CloudGate uses JWT (JSON Web Tokens) for authentication.</p>
          
          <h4 className="text-xl font-bold mb-2">JWT Token Structure</h4>
          <p className="mb-4">Tokens contain the following claims:</p>
          <ul className="list-disc ml-8 mb-6">
            <li><code>uid</code> - User identifier</li>
            <li><code>exp</code> - Token expiration time</li>
            <li><code>iat</code> - Token issue time</li>
          </ul>
          
          <h4 className="text-xl font-bold mb-2">Best Practices</h4>
          <ul className="list-disc ml-8 mb-6">
            <li>Use strong, unique signing keys</li>
            <li>Implement token refresh mechanisms</li>
            <li>Store tokens securely on the client side</li>
            <li>Always validate tokens on the server</li>
          </ul>
          
          <h4 className="text-xl font-bold mb-2">Role-Based Access Control</h4>
          <p className="mb-4">CloudGate supports role-based access with administrator and regular user roles. Administrator access is required for sensitive operations like accessing system keys.</p>
        </section>
      </main>
    );
}
