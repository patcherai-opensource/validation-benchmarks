import S3Image from "../components/S3Image";

export default async function AboutPage() {
    return (
        <main className="flex-grow container mx-auto px-4 py-24 text-center pt-24">
        <section className="mb-16">
          <h2 className="text-4xl font-bold mb-4">About CloudGate</h2>
          <p className="text-xl mb-8">CloudGate is a leading provider of enterprise cloud management solutions, trusted by organizations worldwide.</p>
          
          <div className="text-left max-w-3xl mx-auto mt-12">
            <h3 className="text-2xl font-bold mb-4">Our Mission</h3>
            <p className="mb-6">We strive to simplify cloud infrastructure management while maintaining the highest security standards. Our platform integrates with all major cloud providers to give you complete control over your resources.</p>
            
            <h3 className="text-2xl font-bold mb-4">Security First</h3>
            <p className="mb-6">Security is at the core of everything we do. CloudGate implements industry-leading authentication mechanisms, including JWT-based token authentication, to ensure secure access to your resources.</p>
            
            <h3 className="text-2xl font-bold mb-4">Our Team</h3>
            <p className="mb-6">Our team consists of experienced cloud architects, security experts, and software engineers dedicated to building the best cloud management platform.</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mt-12">
            <div className="bg-white shadow-lg rounded-lg text-black p-6">
              <S3Image src="/will_rogers.jpg" alt="" className="w-full object-cover rounded-t-lg mb-4" />
              <h4 className="text-2xl font-bold mb-2">Will Rogers</h4>
              <p className="text-lg mb-4">Chief Executive Officer</p>
            </div>

            <div className="bg-white shadow-lg rounded-lg text-black p-6">
              <S3Image src="/chris_paulman.jpg" alt="" className="w-full object-cover rounded-t-lg mb-4" />
              <h4 className="text-2xl font-bold mb-2">Christian Paulman</h4>
              <p className="text-lg mb-4">Chief Technology Officer</p>
            </div>

            <div className="bg-white shadow-lg rounded-lg text-black p-6">
              <S3Image src="/julia_mattarazo.jpg" alt="" className="w-full object-cover rounded-t-lg mb-4" />
              <h4 className="text-2xl font-bold mb-2">Julia Mattarazo</h4>
              <p className="text-lg mb-4">Chief Operations Officer</p>
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
