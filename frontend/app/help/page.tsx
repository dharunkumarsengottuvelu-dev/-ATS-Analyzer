'use client';
import { HelpCircle, FileText, Search, Mail, MessageCircle } from 'lucide-react';

export default function HelpPage() {
  return (
    <div className="flex flex-col gap-8 max-w-5xl mx-auto pb-12 w-full">
      <header className="flex flex-col gap-6 border-b border-zinc-800 pb-8 text-center items-center">
        <h1 className="text-4xl font-bold tracking-tight text-zinc-100 mt-4">How can we help you?</h1>
        <p className="text-zinc-400 max-w-lg">Search our knowledge base or browse categories below to find answers to your questions.</p>
        
        <div className="flex items-center gap-4 w-full max-w-2xl bg-zinc-900 border border-zinc-800 rounded-full px-6 py-4 text-zinc-300 focus-within:border-blue-500 focus-within:ring-1 focus-within:ring-blue-500 transition-all shadow-lg mt-4">
            <Search className="w-5 h-5 text-zinc-500" />
            <input 
                type="text" 
                placeholder="Search for articles, guides, or FAQs..." 
                className="bg-transparent border-none outline-none flex-1 text-base placeholder-zinc-500"
            />
        </div>
      </header>

      <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-4">
          <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-xl flex flex-col gap-4 hover:border-zinc-700 transition-colors cursor-pointer group">
              <div className="w-12 h-12 bg-blue-500/10 text-blue-500 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                  <FileText className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-semibold text-zinc-100">Getting Started</h3>
              <p className="text-zinc-400 text-sm">Learn how to upload your first resume and configure your ATS settings.</p>
          </div>
          <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-xl flex flex-col gap-4 hover:border-zinc-700 transition-colors cursor-pointer group">
              <div className="w-12 h-12 bg-purple-500/10 text-purple-500 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                  <HelpCircle className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-semibold text-zinc-100">FAQ</h3>
              <p className="text-zinc-400 text-sm">Answers to common questions about scoring, keywords, and exports.</p>
          </div>
          <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-xl flex flex-col gap-4 hover:border-zinc-700 transition-colors cursor-pointer group">
              <div className="w-12 h-12 bg-green-500/10 text-green-500 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                  <MessageCircle className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-semibold text-zinc-100">AI Models</h3>
              <p className="text-zinc-400 text-sm">Documentation on switching between local LLMs and OpenAI.</p>
          </div>
      </section>

      <section className="mt-8 flex flex-col gap-6">
          <h2 className="text-2xl font-bold text-zinc-100">Frequently Asked Questions</h2>
          <div className="flex flex-col gap-4">
              <details className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 group open:bg-zinc-900/80 transition-colors">
                  <summary className="font-medium text-zinc-200 cursor-pointer list-none flex justify-between items-center">
                      What formats are supported for resume upload?
                      <span className="transition group-open:rotate-180">
                          <svg fill="none" height="24" shapeRendering="geometricPrecision" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" viewBox="0 0 24 24" width="24"><path d="M6 9l6 6 6-6"></path></svg>
                      </span>
                  </summary>
                  <p className="text-zinc-400 mt-4 text-sm leading-relaxed">
                      We currently support PDF, DOCX, and TXT files up to 20MB in size. We recommend PDF for the best parsing accuracy.
                  </p>
              </details>
              
              <details className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 group open:bg-zinc-900/80 transition-colors">
                  <summary className="font-medium text-zinc-200 cursor-pointer list-none flex justify-between items-center">
                      How is the ATS Score calculated?
                      <span className="transition group-open:rotate-180">
                          <svg fill="none" height="24" shapeRendering="geometricPrecision" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" viewBox="0 0 24 24" width="24"><path d="M6 9l6 6 6-6"></path></svg>
                      </span>
                  </summary>
                  <p className="text-zinc-400 mt-4 text-sm leading-relaxed">
                      The ATS score is a proprietary algorithm that calculates keyword density, exact phrase matching, formatting strictness, and section presence compared to the provided Job Description. A score above 80% is considered highly optimized.
                  </p>
              </details>
          </div>
      </section>
      
      <section className="mt-8 p-8 border border-zinc-800 bg-blue-950/20 rounded-2xl flex flex-col items-center text-center gap-4">
          <Mail className="w-10 h-10 text-blue-500 mb-2" />
          <h2 className="text-2xl font-bold text-zinc-100">Still need help?</h2>
          <p className="text-zinc-400">Our support team is available 24/7 to assist enterprise customers.</p>
          <button className="mt-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-xl transition-all shadow-lg shadow-blue-500/20">
              Contact Support
          </button>
      </section>
    </div>
  );
}
