import React, { useRef } from 'react';
import { Link } from 'react-router-dom';
import { useLandingEffects } from '@/hooks/useLandingEffects';
import '@/styles/landing.css';

const cssVar = (d: string): React.CSSProperties => ({ ['--d' as string]: d });
const cssI = (i: number): React.CSSProperties => ({ ['--i' as string]: i });

export const LandingPage: React.FC = () => {
  const rootRef = useRef<HTMLDivElement>(null);
  useLandingEffects(rootRef);

  return (
    <div className="landing-page" ref={rootRef}>
      <div id="bar" />
      <div id="glow" />
      <div id="side" aria-hidden="true">
        <a href="#hero" />
        <a href="#framework" />
        <a href="#how" />
        <a href="#security" />
        <a href="#platforms" />
        <a href="#steps" />
        <a href="#research" />
      </div>

      <nav id="nav">
        <a href="#hero" className="logo">
          <span className="dot" />
          ARYACRYPT
        </a>
        <button id="burger" aria-label="Menu" aria-expanded="false" type="button">
          <i />
          <i />
        </button>
        <div className="links" id="links">
          <a href="#framework">Framework</a>
          <a href="#how">How It Works</a>
          <a href="#security">Security</a>
          <a href="#platforms">Platforms</a>
          <Link to="/login">Log In</Link>
          <Link to="/register" className="btn p sm">
            Get Started
          </Link>
        </div>
      </nav>

      <main>
        <section id="hero">
          <div className="bg">
            <div className="grid" />
            <div className="halo" />
            <div className="orb" />
            <canvas id="cv" />
          </div>
          <div className="hc">
            <p className="tag">CRYPTOGRAPHIC SECURITY FRAMEWORK · SPEC v1.1.0</p>
            <h1 className="wm" aria-label="ARYACRYPT" />
            <p className="sub">Cryptographic Security Framework</p>
            <p className="sup">
              Password preprocessing and key generation for AES-256-GCM — Aryabhata-inspired
              diffusion before PBKDF2, without replacing established cryptography.
            </p>
            <div className="cta">
              <Link to="/register" className="btn p mag">
                Start Encrypting <span className="ar">→</span>
              </Link>
              <a href="#framework" className="btn g dn mag">
                Explore Framework <span className="ar">↓</span>
              </a>
            </div>
          </div>
        </section>

        <div className="mq" aria-hidden="true">
          <div className="mq-track">
            {[0, 1].map((copy) => (
              <div className="mq-group" key={copy}>
                <span>Aryabhata Base-100</span>
                <span className="sep">✦</span>
                <span>PBKDF2-HMAC-SHA256</span>
                <span className="sep">✦</span>
                <span>AES-256-GCM</span>
                <span className="sep">✦</span>
                <span>Portable .arya</span>
                <span className="sep">✦</span>
                <span>Spec v1.1.0</span>
                <span className="sep">✦</span>
                <span>Cross-language vectors</span>
                <span className="sep">✦</span>
              </div>
            ))}
          </div>
        </div>
        <div className="mq mq-rev" aria-hidden="true">
          <div className="mq-track">
            {[0, 1].map((copy) => (
              <div className="mq-group" key={copy}>
                <span>Unicode NFC</span>
                <span className="sep">→</span>
                <span>RomanMapper</span>
                <span className="sep">→</span>
                <span>600,000 iterations</span>
                <span className="sep">→</span>
                <span>16-byte salt</span>
                <span className="sep">→</span>
                <span>12-byte nonce</span>
                <span className="sep">→</span>
                <span>.arya container</span>
                <span className="sep">→</span>
              </div>
            ))}
          </div>
        </div>

        <section id="pipe">
          <div className="wrap">
            <div className="label rv">THE PIPELINE</div>
            <h2 className="rv" style={cssVar('.1s')}>
              Six stages. One deterministic path.
            </h2>
            <div className="pl rv" id="pl" style={cssVar('.2s')}>
              <div className="pk" id="pk" />
              <div className="nd">
                <small>00</small>
                <b>PASSWORD</b>
                <p>The only secret. Supplied by the user, never stored.</p>
              </div>
              <div className="nd">
                <small>01</small>
                <b>NFC</b>
                <p>Unicode normalization so equal text yields equal bytes.</p>
              </div>
              <div className="nd">
                <small>02</small>
                <b>ARYABHATA</b>
                <p>Base-100 RomanMapper turns text into a phonetic stream.</p>
              </div>
              <div className="nd">
                <small>03</small>
                <b>PBKDF2</b>
                <p>HMAC-SHA256, 600,000 iterations, random 16-byte salt.</p>
              </div>
              <div className="nd">
                <small>04</small>
                <b>AES-256-GCM</b>
                <p>Authenticated encryption with a fresh 12-byte nonce.</p>
              </div>
              <div className="nd">
                <small>05</small>
                <b>.ARYA</b>
                <p>Portable, versioned container for the encrypted output.</p>
              </div>
            </div>
          </div>
        </section>

        <section id="framework">
          <div className="wrap two">
            <div>
              <div className="label rv">FRAMEWORK</div>
              <div className="big rv" style={cssVar('.1s')}>
                What is
                <br />
                AryaCrypt<em>?</em>
              </div>
              <div className="chain rv" style={cssVar('.25s')}>
                Unicode NFC <span>→</span> Aryabhata Base-100
                <br />
                RomanMapper <span>→</span> PBKDF2-HMAC-SHA256
                <br />
                <span>→</span> AES-256-GCM <span>→</span> .arya
              </div>
            </div>
            <div className="vl" />
            <div className="rv r" style={cssVar('.2s')}>
              <p className="lead">
                AryaCrypt is a cryptographic security framework that transforms a password through
                an Aryabhata-inspired RomanMapper pipeline before key derivation. The resulting
                stream feeds standard PBKDF2-HMAC-SHA256 (600,000 iterations), which produces the
                key for AES-256-GCM file encryption. Output is packaged in the portable{' '}
                <code className="mono" style={{ color: 'var(--cy)' }}>
                  .arya
                </code>{' '}
                container format.
              </p>
            </div>
          </div>
        </section>

        <section id="built">
          <div className="wrap">
            <div className="label rv">PRIMITIVES</div>
            <h2 className="rv" style={cssVar('.1s')}>
              Built around established cryptography.
            </h2>
            <div className="cards">
              <article className="card rv" style={cssVar('0s')}>
                <span className="n">01</span>
                <h3>Aryabhata Preprocessing</h3>
                <p>Unicode normalization and Base-100 phonetic mapping before key derivation.</p>
              </article>
              <article className="card rv" style={cssVar('.12s')}>
                <span className="n">02</span>
                <h3>PBKDF2-HMAC-SHA256</h3>
                <p>600,000 iterations with a fresh 16-byte salt.</p>
              </article>
              <article className="card rv" style={cssVar('.24s')}>
                <span className="n">03</span>
                <h3>AES-256-GCM</h3>
                <p>Authenticated encryption with a fresh 12-byte nonce.</p>
              </article>
              <article className="card rv" style={cssVar('.36s')}>
                <span className="n">04</span>
                <h3>Portable .arya</h3>
                <p>Versioned encrypted container format.</p>
              </article>
            </div>
          </div>
        </section>

        <section id="how">
          <div className="wrap">
            <div className="label rv">PROCESS</div>
            <h2 className="rv" style={cssVar('.1s')}>
              How it works
            </h2>
            <div className="stk">
              <div className="stc" style={cssI(0)}>
                <div className="nn">1</div>
                <div>
                  <h3>Preprocess</h3>
                  <p>
                    Unicode NFC normalization and Aryabhata Base-100 phonetic diffusion
                    (RomanMapper).
                  </p>
                  <span className="tg">NFC + RomanMapper</span>
                </div>
              </div>
              <div className="stc" style={cssI(1)}>
                <div className="nn">2</div>
                <div>
                  <h3>Derive</h3>
                  <p>
                    PBKDF2-HMAC-SHA256 with a random 16-byte salt, 600,000 iterations, 32-byte key.
                  </p>
                  <span className="tg">600,000 iterations</span>
                </div>
              </div>
              <div className="stc" style={cssI(2)}>
                <div className="nn">3</div>
                <div>
                  <h3>Encrypt</h3>
                  <p>AES-256-GCM with a random 12-byte nonce and authenticated ciphertext.</p>
                  <span className="tg">AES-256-GCM</span>
                </div>
              </div>
              <div className="stc" style={cssI(3)}>
                <div className="nn">4</div>
                <div>
                  <h3>Package</h3>
                  <p>Serialize metadata and ciphertext into a versioned .arya file.</p>
                  <span className="tg">.arya container</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section id="security">
          <div className="wrap">
            <div className="label rv">SECURITY</div>
            <h2 className="rv" style={{ ...cssVar('.1s'), marginBottom: 40 }}>
              Security architecture
            </h2>
            <p className="quote rv l" style={cssVar('.15s')}>
              AryaCrypt does not invent a new cipher. It adds a deterministic preprocessing layer
              ahead of well-studied primitives so that key material is derived from a transformed
              password stream rather than raw UTF-8 password bytes.
            </p>
            <div className="stats">
              <div>
                <b data-n="600000" data-s="">
                  600,000
                </b>
                <small>PBKDF2 iterations</small>
              </div>
              <div>
                <b data-n="32" data-s="-byte">
                  32-byte
                </b>
                <small>derived key (AES-256)</small>
              </div>
              <div>
                <b data-n="16" data-s="-byte">
                  16-byte
                </b>
                <small>fresh random salt</small>
              </div>
              <div>
                <b data-n="12" data-s="-byte">
                  12-byte
                </b>
                <small>fresh random nonce</small>
              </div>
            </div>
            <div className="specs rv s">
              <div className="sp">
                <small>CIPHER</small>
                <b>AES-256-GCM</b>
              </div>
              <div className="sp">
                <small>KDF</small>
                <b>PBKDF2-HMAC-SHA256</b>
              </div>
              <div className="sp">
                <small>WORK FACTOR</small>
                <b>600,000 iterations</b>
              </div>
              <div className="sp">
                <small>SALT</small>
                <b>16-byte</b>
              </div>
              <div className="sp">
                <small>NONCE</small>
                <b>12-byte</b>
              </div>
              <div className="sp">
                <small>SPECIFICATION</small>
                <b>Spec v1.1.0</b>
              </div>
              <div className="sp">
                <small>VERIFICATION</small>
                <b>Cross-language test vectors</b>
              </div>
              <div className="sp">
                <small>SECRET</small>
                <b>The password alone</b>
              </div>
            </div>

            <div className="term rv s" style={cssVar('.1s')}>
              <div className="th">
                <span>ARYACRYPT // PYTHON SDK</span>
                <span>Python SDK</span>
                <button className="copy" id="copy" type="button">
                  Copy
                </button>
              </div>
              <pre>
                <code id="code" />
                <span className="cur" />
              </pre>
            </div>
          </div>
        </section>

        <section id="platforms">
          <div className="wrap">
            <div className="label rv">PLATFORMS</div>
            <h2 className="rv" style={cssVar('.1s')}>
              One format. Multiple environments.
            </h2>
            <div className="plat">
              <div className="pf rv tilt" style={cssVar('0s')}>
                <div className="num">01</div>
                <h3>Python SDK</h3>
                <p>
                  Encrypt and decrypt <code className="mono">.arya</code> files using the same
                  specification.
                </p>
              </div>
              <div className="pf rv tilt" style={cssVar('.15s')}>
                <div className="num">02</div>
                <h3>Node.js SDK</h3>
                <p>TypeScript SDK with the same format and vectors.</p>
              </div>
              <div className="pf rv tilt" style={cssVar('.3s')}>
                <div className="num">03</div>
                <h3>Web Vault</h3>
                <p>
                  Authenticated vault for encryption, decryption, storage, analytics and account
                  settings.
                </p>
              </div>
            </div>
          </div>
        </section>

        <section id="steps">
          <div className="wrap sg">
            <div>
              <div className="label rv">LIVE VISUALIZER</div>
              <h2 className="rv" style={{ ...cssVar('.1s'), marginBottom: 26 }}>
                See every step.
              </h2>
              <p className="lead rv" style={cssVar('.2s')}>
                On Encrypt and Decrypt, the web app shows the live pipeline: NFC → seed → Aryabhata
                phonetic stream → salt/nonce → PBKDF2 → AES-GCM →{' '}
                <code className="mono">.arya</code> packing.
              </p>
            </div>
            <div className="mock rv r" style={cssVar('.2s')} id="mock">
              <h4>
                <span>ENCRYPTION PIPELINE</span>
                <i id="mst">IDLE</i>
              </h4>
              <div className="row">
                <span className="ic">○</span>Unicode NFC
              </div>
              <div className="arw" />
              <div className="row">
                <span className="ic">○</span>RomanMapper
              </div>
              <div className="arw" />
              <div className="row">
                <span className="ic">○</span>PBKDF2-HMAC-SHA256
              </div>
              <div className="arw" />
              <div className="row">
                <span className="ic">○</span>AES-256-GCM
              </div>
              <div className="arw" />
              <div className="row">
                <span className="ic">○</span>.ARYA PACKAGE
              </div>
              <div className="meter">
                <i id="mt" />
              </div>
            </div>
          </div>
        </section>

        <section id="research">
          <div className="bgt" aria-hidden="true">
            <span style={{ left: '6%', top: '12%', fontSize: 180 }}>100</span>
            <span style={{ left: '74%', top: '6%', fontSize: 120, ['--dl' as string]: '-6s' }}>
              0
            </span>
            <span style={{ left: '84%', top: '58%', fontSize: 200, ['--dl' as string]: '-12s' }}>
              1
            </span>
            <span style={{ left: '12%', top: '62%', fontSize: 150, ['--dl' as string]: '-3s' }}>
              2
            </span>
            <span style={{ left: '46%', top: '78%', fontSize: 110, ['--dl' as string]: '-9s' }}>
              3
            </span>
            <span
              style={{ left: '30%', top: '2%', fontSize: 54, ['--dl' as string]: '-14s' }}
            >
              ARYABHATA
            </span>
            <span
              style={{ left: '58%', top: '88%', fontSize: 54, ['--dl' as string]: '-18s' }}
            >
              ROMANMAPPER
            </span>
          </div>
          <div className="wrap">
            <div className="label rv" style={{ justifyContent: 'center' }}>
              RESEARCH
            </div>
            <h2 className="rv" style={cssVar('.1s')}>
              Where classical mathematics meets modern cryptography.
            </h2>
            <p className="lead rv" style={cssVar('.25s')}>
              AryaCrypt explores historical Aryabhata alphasyllabic encoding as a software diffusion
              step before modern KDF usage — bridging classical Indian mathematics with practical
              file encryption tooling.
            </p>
          </div>
        </section>

        <section id="stack" style={{ paddingBlock: '70px 40px' }}>
          <div className="wrap">
            <div className="label rv">TECHNOLOGY STACK</div>
            <div className="pills">
              <span className="pill rv" style={cssVar('0s')}>
                React + Vite
              </span>
              <span className="pill rv" style={cssVar('.07s')}>
                FastAPI
              </span>
              <span className="pill rv" style={cssVar('.14s')}>
                PostgreSQL
              </span>
              <span className="pill rv" style={cssVar('.21s')}>
                Python SDK
              </span>
              <span className="pill rv" style={cssVar('.28s')}>
                Node SDK
              </span>
              <span className="pill rv" style={cssVar('.35s')}>
                Spec v1.1.0
              </span>
              <span className="pill rv" style={cssVar('.42s')}>
                Cross-language Test Vectors
              </span>
            </div>
          </div>
        </section>

        <section id="final">
          <div className="wrap">
            <h2 className="rv">
              Your password.
              <br />
              Your data.
              <br />
              Your <code>.arya</code>
            </h2>
            <p className="rv" style={cssVar('.15s')}>
              Explore the framework and start encrypting.
            </p>
            <div className="cta rv" style={{ ...cssVar('.3s'), opacity: 1, animation: 'none' }}>
              <Link to="/register" className="btn p mag">
                Start Encrypting <span className="ar">→</span>
              </Link>
              <a href="#framework" className="btn g mag">
                Explore Framework
              </a>
            </div>
          </div>
        </section>
      </main>

      <footer>
        <div className="wrap">
          <div className="fg">
            <div>
              <div className="logo">
                <span className="dot" />
                ARYACRYPT
              </div>
              <p>Cryptographic Security Framework</p>
              <span className="mono">v1.1.0</span>
            </div>
            <div className="fl">
              <a href="#framework">Framework</a>
              <a href="#security">Security</a>
              <a href="#platforms">Platforms</a>
              <Link to="/login">Login</Link>
            </div>
          </div>
          <div className="cp">© 2026 AryaCrypt. All rights reserved.</div>
        </div>
      </footer>
    </div>
  );
};
