import React from 'react';

const items = [
  {
    title: 'AES-256-GCM',
    body: 'Authenticated encryption for file payloads with a fresh nonce per operation.',
  },
  {
    title: 'Aryabhata preprocessing',
    body: 'RomanMapper phonetic diffusion applied before key derivation on the current algorithm path.',
  },
  {
    title: 'PBKDF2-HMAC-SHA256',
    body: '600,000 iterations with a 16-byte salt producing a 32-byte encryption key.',
  },
  {
    title: '.arya container',
    body: 'Versioned header and ciphertext format shared by the Python and Node SDKs.',
  },
];

/** Alternate features block (not mounted). Accurate copy only. */
export const FeaturesSection: React.FC = () => {
  return (
    <section className="py-16 border-t border-border/40">
      <div className="container mx-auto px-4 max-w-5xl">
        <h2 className="text-2xl font-bold text-slate-100 mb-8 text-center">
          Cryptographic architecture
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {items.map((item) => (
            <div key={item.title} className="border border-border/60 rounded-lg p-5 bg-card/30">
              <h3 className="font-semibold text-slate-100 mb-2">{item.title}</h3>
              <p className="text-sm text-slate-400 leading-relaxed">{item.body}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
