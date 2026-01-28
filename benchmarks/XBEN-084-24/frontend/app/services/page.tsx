export default async function ServicesPage() {
    return (
        <main className="flex-grow container mx-auto px-4 py-24 text-center pt-24">
        <section className="mb-16">
          <h2 className="text-4xl font-bold mb-4">Our Services</h2>
          <p className="text-xl mb-8">Comprehensive cloud management solutions for enterprises of all sizes.</p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mt-12 max-w-4xl mx-auto">
            <div className="bg-gray-800 p-6 rounded-lg text-left">
              <h3 className="text-2xl font-bold mb-4">Cloud Orchestration</h3>
              <p>Automated deployment and management of cloud resources across multiple providers including AWS, Azure, and GCP.</p>
            </div>
            
            <div className="bg-gray-800 p-6 rounded-lg text-left">
              <h3 className="text-2xl font-bold mb-4">Security & Compliance</h3>
              <p>Enterprise-grade security with role-based access control, audit logging, and compliance reporting.</p>
            </div>
            
            <div className="bg-gray-800 p-6 rounded-lg text-left">
              <h3 className="text-2xl font-bold mb-4">Monitoring & Analytics</h3>
              <p>Real-time monitoring, alerting, and comprehensive analytics for your entire infrastructure.</p>
            </div>
            
            <div className="bg-gray-800 p-6 rounded-lg text-left">
              <h3 className="text-2xl font-bold mb-4">API Gateway</h3>
              <p>Secure API management with JWT authentication, rate limiting, and request transformation capabilities.</p>
            </div>
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
